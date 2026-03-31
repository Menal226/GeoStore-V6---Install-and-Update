import queue
import sys
import threading
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

from requests import Session

from enums.module import Module, get_module_config, get_module_from_selection_key, get_module_order
from gui.stdout_mirror import StdoutMirror
from services.auth import Authenticator
from services.checker import Checker
from services.installer import Installer
from startup.cli_args import parse_startup_args


class GeoStoreWindow(tk.Tk):
    def __init__(self, args: list[str] | None = None) -> None:
        super().__init__()
        self.title("GeoStore - Update and Install")
        self._set_window_icon()
        self.geometry("760x680")
        self.minsize(760, 680)
        self.maxsize(760, 680)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._module_order = get_module_order()

        self._session = Session()
        self._auth = Authenticator(self._session)
        self._checker = Checker(self._session)
        self._installer = Installer(self._session)

        self._is_logged_in = False
        self._workflow_running = False

        startup_args = parse_startup_args(args)
        self._startup_username = startup_args.username
        self._startup_password = startup_args.password
        self._startup_selection = startup_args.selection

        self.checkbox_vars: dict[Module, tk.BooleanVar] = {}
        self.module_checkboxes: dict[Module, ttk.Checkbutton] = {}
        self.status_labels: dict[Module, ttk.Label] = {}
        self.name_labels: dict[Module, ttk.Label] = {}

        container = self._make_container()

        top_row = ttk.Frame(container)
        top_row.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        top_row.grid_columnconfigure(0, weight=3)
        top_row.grid_columnconfigure(1, weight=2)

        self._login_setup(top_row)
        self._module_selection_setup(top_row)
        self._stdout_mirror_setup(container)

        self._apply_startup_values()

    def _set_window_icon(self) -> None:
        icon_path = Path(__file__).resolve().parents[2] / "icon.ico"
        if not icon_path.exists():
            return

        try:
            self.iconbitmap(str(icon_path))
        except tk.TclError:
            # Keep default icon if the runtime cannot load .ico.
            pass

    def _apply_startup_values(self) -> None:
        if self._startup_username:
            self.username_var.set(self._startup_username)
        if self._startup_password:
            self.password_var.set(self._startup_password)
        if self._startup_selection:
            self._apply_selection_string(self._startup_selection)

        if self._startup_username and self._startup_password:
            self.after(50, self._on_login)

    def _apply_selection_string(self, selected: str) -> None:
        for char in selected:
            module = get_module_from_selection_key(char)
            if module is None or module not in self.checkbox_vars:
                continue

            current = self.checkbox_vars[module].get()
            self.checkbox_vars[module].set(not current)

    def _module_selection_setup(self, frame: ttk.Frame) -> None:
        selection_frame = ttk.LabelFrame(frame, text="Výběr Modulů", padding=8)
        selection_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        selection_frame.grid_columnconfigure(0, weight=1)
        selection_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(selection_frame, text="Stav", font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=0, padx=6, pady=(0, 4), sticky="w"
        )
        ttk.Label(selection_frame, text="Modul", font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=1, padx=6, pady=(0, 4), sticky="w"
        )
        ttk.Label(selection_frame, text="Vybrat", font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=2, padx=6, pady=(0, 4), sticky="w"
        )

        for row_index, module in enumerate(self._module_order, start=1):
            left_label = ttk.Label(selection_frame, text="Vyžaduje přihlášení", font=("TkDefaultFont", 10, "bold"))
            right_label = ttk.Label(selection_frame, text=self._get_label_name(module))

            checked = tk.BooleanVar(value=False)
            checkbox = ttk.Checkbutton(selection_frame, variable=checked, state="disabled")

            self.status_labels[module] = left_label
            self.name_labels[module] = right_label
            self.checkbox_vars[module] = checked
            self.module_checkboxes[module] = checkbox

            left_label.grid(row=row_index, column=0, padx=6, pady=4, sticky="w")
            right_label.grid(row=row_index, column=1, padx=6, pady=4, sticky="w")
            checkbox.grid(row=row_index, column=2, padx=6, pady=4, sticky="w")

        selection_buttons = ttk.Frame(selection_frame)
        selection_buttons.grid(row=len(self._module_order) + 1, column=0, columnspan=3, pady=(8, 0), sticky="e")

        self.update_button = ttk.Button(selection_buttons, text="Aktualizovat", command=self._on_update)
        self.update_button.grid(row=0, column=0, padx=(0, 8))
        self.update_button.configure(state="disabled")

        self.install_button = ttk.Button(selection_buttons, text="Instalovat", command=self._on_install)
        self.install_button.grid(row=0, column=1, padx=(0, 8))
        self.install_button.configure(state="disabled")

    def _on_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            print("Vyplňte uživatelské jméno a heslo.")
            return

        if not self._auth.login(username, password):
            self._is_logged_in = False
            self.password_var.set("")
            self._set_module_controls_enabled(False)
            self._set_logged_out_labels()
            return

        self._is_logged_in = True
        self._set_module_controls_enabled(not self._workflow_running)
        self._refresh_module_labels()
        print("Přihlášení proběhlo úspěšně.")

    def _collect_selected_modules(self) -> dict[Module, bool]:
        return {module: variable.get() for module, variable in self.checkbox_vars.items()}

    def _on_update(self) -> None:
        self._run_installer_workflow(is_install=False)

    def _on_install(self) -> None:
        self._run_installer_workflow(is_install=True)

    def _run_installer_workflow(self, is_install: bool) -> None:
        if not self._is_logged_in:
            print("Nejprve se přihlaste.")
            return
        if self._workflow_running:
            print("Již probíhá jiná operace, počkejte na dokončení.")
            return

        selected = self._collect_selected_modules()
        if not any(selected.values()):
            print("Nevybrali jste žádný modul.")
            return

        action_text = "instalaci" if is_install else "aktualizaci"
        if not messagebox.askyesno("Potvrzení", f"Opravdu chcete spustit {action_text} vybraných modulů?"):
            return

        self._workflow_running = True
        self._set_module_controls_enabled(False)
        print(f"Spouštím {'instalaci' if is_install else 'aktualizaci'} vybraných modulů...")

        worker = threading.Thread(target=self._execute_installer_workflow, args=(selected, is_install), daemon=True)
        worker.start()

    def _execute_installer_workflow(self, selected: dict[Module, bool], is_install: bool) -> None:
        processed = self._installer.start_downloads(selected, is_install)

        failed_time = datetime.fromtimestamp(0)
        for module in processed:
            newest = self._checker.get_newest_update_time(module)
            if newest != failed_time:
                self._checker.update_last_saved_time(module, newest)

        self.after(0, lambda: self._on_workflow_finished(processed, is_install))

    def _on_workflow_finished(self, processed: list[Module], is_install: bool) -> None:
        self._workflow_running = False
        self._set_module_controls_enabled(self._is_logged_in)

        if self._is_logged_in:
            self._refresh_module_labels()

        print(
            f"{'Instalace' if is_install else 'Aktualizace'} dokončena. "
            f"Úspěšně zpracováno modulů: {len(processed)}"
        )

    def _set_module_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"

        for checkbox in self.module_checkboxes.values():
            checkbox.configure(state=state)

        self.update_button.configure(state=state)
        self.install_button.configure(state=state)

    def _refresh_module_labels(self) -> None:
        statuses = self._checker.get_update_status()
        for module in self._module_order:
            status_text, color = self._get_status_label(statuses.get(module))
            self.status_labels[module].configure(text=status_text, foreground=color, font=("TkDefaultFont", 10, "normal"))
            self.name_labels[module].configure(text=self._get_label_name(module))

    def _set_logged_out_labels(self) -> None:
        for module in self._module_order:
            self.status_labels[module].configure(text="Vyžaduje přihlášení", foreground="black")
            self.name_labels[module].configure(text=self._get_label_name(module))

    def _get_status_label(self, status: bool | None) -> tuple[str, str]:
        if status is False:
            return "Nejnovější verze", "green"
        if status is True:
            return "Stará verze", "red"
        return "Nelze ověřit verzi", "orange"

    def _get_label_name(self, module: Module) -> str:
        return get_module_config(module).display_name

    def _stdout_mirror_setup(self, container: ttk.Frame) -> None:
        frame = ttk.LabelFrame(container, text="Informace O Průběhu Instalace", padding=8)
        frame.grid(row=1, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        self.stdout_text = tk.Text(frame, wrap="word", state="disabled")
        self.stdout_text.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.stdout_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.stdout_text.configure(yscrollcommand=scrollbar.set)

        self._stdout_queue: "queue.Queue[str]" = queue.Queue()
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self._stdout_mirror = StdoutMirror(self._original_stdout, self._stdout_queue)
        self._stderr_mirror = StdoutMirror(self._original_stderr, self._stdout_queue)
        sys.stdout = self._stdout_mirror
        sys.stderr = self._stderr_mirror

        self._poll_job = self.after(100, self._poll_stdout)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _poll_stdout(self) -> None:
        try:
            while True:
                chunk = self._stdout_queue.get_nowait()
                self.stdout_text.configure(state="normal")
                self.stdout_text.insert("end", chunk)
                self.stdout_text.see("end")
                self.stdout_text.configure(state="disabled")
        except queue.Empty:
            pass

        self._poll_job = self.after(100, self._poll_stdout)

    def _on_close(self) -> None:
        if not messagebox.askyesno("Potvrzení", "Opravdu chcete aplikaci ukončit?"):
            return

        if self._poll_job is not None:
            self.after_cancel(self._poll_job)
            self._poll_job = None

        if sys.stdout is self._stdout_mirror:
            sys.stdout = self._original_stdout
        if sys.stderr is self._stderr_mirror:
            sys.stderr = self._original_stderr

        self._session.close()
        self.destroy()

    def _make_container(self) -> ttk.Frame:
        container = ttk.Frame(self, padding=8)
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        return container

    def _login_setup(self, frame: ttk.Frame) -> None:
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        login_frame = ttk.LabelFrame(frame, text="Přihlášení", padding=8)
        login_frame.grid(row=0, column=0, sticky="nsew")
        login_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(login_frame, text="Uživatelské jméno:").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        username_entry = ttk.Entry(login_frame, textvariable=self.username_var)
        username_entry.grid(row=0, column=1, padx=6, pady=4, sticky="ew")

        ttk.Label(login_frame, text="Heslo:").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        password_entry = ttk.Entry(login_frame, textvariable=self.password_var, show="*")
        password_entry.grid(row=1, column=1, padx=6, pady=4, sticky="ew")

        button_row = ttk.Frame(login_frame)
        button_row.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky="e")

        self.login_button = ttk.Button(button_row, text="Přihlásit", command=self._on_login)
        self.login_button.grid(row=0, column=0)
        username_entry.focus_set()