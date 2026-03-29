from os import system
from keyboard import add_hotkey, clear_all_hotkeys
from enums.module import Module

class SelectionController:
    def __init__(self):
        self._selected: dict[Module, bool] = {
            Module.EDITOR: False,
            Module.DTMCR: False,
            Module.THREED: False,
            Module.IG: False,
            Module.DWG: False,
        }
        self._is_install = False
        self._confirmed = 0

    @property
    def selected(self) -> dict[str, bool]:
        return self._selected

    @property
    def is_install(self) -> bool:
        return self._is_install

    def parse_selected(self, string: str) -> None:
        for char in string:
            match char:
                case "1":
                    self._selected[Module.EDITOR] = not self._selected[Module.EDITOR]
                    continue
                case "2":
                    self._selected[Module.DTMCR] = not self._selected[Module.DTMCR]
                    continue
                case "3":
                    self._selected[Module.IG] = not self._selected[Module.IG]
                    continue
                case "4":
                    self._selected[Module.THREED] = not self._selected[Module.THREED]
                    continue
                case "5":
                    self._selected[Module.DWG] = not self._selected[Module.DWG]
                    continue
                case "6":
                    self._is_install = not self._is_install
                    continue
                case _:
                    continue

    def select_wanted(self) -> None:
        add_hotkey("num 1", self._switch_selection, args=(Module.EDITOR,))
        add_hotkey("num 2", self._switch_selection, args=(Module.DTMCR,))
        add_hotkey("num 3", self._switch_selection, args=(Module.IG,))
        add_hotkey("num 4", self._switch_selection, args=(Module.THREED,))
        add_hotkey("num 5", self._switch_selection, args=(Module.DWG,))
        add_hotkey("num 6", self._switch_install)
        add_hotkey("num enter", self._enter_process)
        self._redraw_selection()

        while self._confirmed != 2:
            ...

        clear_all_hotkeys()
        system("cls")

    def _redraw_selection(self) -> None:
        system("cls")
        print(
            f"Pomocí čísel 1-5 vyberte, které programy si přejete {'aktualizovat' if self._is_install else 'instalovat'}."
        )
        print("Pomocí čísla 6 můžete přepínat mezi aktualizací a novou instalací!")
        print("Pro potvrzení stiskněte ENTER")
        print()
        print(
            f"1. [{'X' if self._selected[Module.EDITOR] else ' '}] {'Instalace' if self._is_install else 'Aktualizace'} Základního Grafického Editoru"
        )
        print(
            f"2. [{'X' if self._selected[Module.DTMCR] else ' '}] {'Instalace' if self._is_install else 'Aktualizace'} Aplikace DTMČR"
        )
        print(
            f"3. [{'X' if self._selected[Module.IG] else ' '}] {'Instalace' if self._is_install else 'Aktualizace'} Aplikace IG"
        )
        print(
            f"4. [{'X' if self._selected[Module.THREED] else ' '}] {'Instalace' if self._is_install else 'Aktualizace'} Aplikace 3D"
        )
        print(
            f"5. [{'X' if self._selected[Module.DWG] else ' '}] {'Instalace' if self._is_install else 'Aktualizace'} Aplikace DWG"
        )
        print(f"6. Přepnout do režimu {'Aktualizace' if self._is_install else 'Nové Instalace'}")

    def _switch_selection(self, name: str) -> None:
        self._selected[name] = not self._selected[name]
        self._confirmed = 0
        self._redraw_selection()

    def _switch_install(self) -> None:
        self._is_install = not self._is_install
        self._confirmed = 0
        self._redraw_selection()

    def _enter_process(self) -> None:
        if self._confirmed == 0:
            print("\033[31mPro potvrzení výběru napište stiskněte znovu ENTER\033[0m ")
        self._confirmed += 1
