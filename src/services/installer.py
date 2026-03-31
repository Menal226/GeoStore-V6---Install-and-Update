import sys
from os import path, remove
from shutil import rmtree
from subprocess import run
from zipfile import ZipFile

from requests import Session
from tqdm import tqdm

from enums.module import Module
from resources.urls import (
    D3_FULL_DOWNLOAD_URL,
    D3_PARTIAL_DOWNLOAD_URL,
    DTMCR_FULL_DOWNLOAD_URL,
    DTMCR_PARTIAL_DOWNLOAD_URL,
    DWG_DONWLOAD_URL,
    EDITOR_DOWNLOAD_URL,
    IG_FULL_DOWNLOAD_URL,
    IG_PARTIAL_DOWNLOAD_URL,
)


class Installer:
    def __init__(self, session: Session):
        self._session = session

    def start_downloads(self, selected: dict[Module, bool], is_install: bool) -> list[Module]:
        processed: list[Module] = []
        for key, val in selected.items():
            if not val:
                continue

            module_name = key.value
            try:
                self._download_from_url(key, is_install)
                self._unzip_file(f"C:\\{module_name}.zip", "C:\\", module_name)
                print("Postupujte podle pokynů v novém okně.")
                self._run_program("C:\\V6-INSTALL\\setup.exe" if key == Module.EDITOR else "C:\\V6-INSTALL\\Install.exe")
                if key == Module.EDITOR:
                    self._run_program(r"C:\Program Files\GEOVAP\GeoStoreV6\Redist\vc2010redist_x64.exe")
                    self._run_program(r"C:\Program Files\GEOVAP\GeoStoreV6\Redist\vc2012redist_x64.exe")
                print(f"{'Instalace' if is_install else 'Aktualizace'} {module_name} byla dokončena")
                processed.append(key)
            except Exception as ex:
                print(
                    f"Při {'instalaci' if is_install else 'aktualizaci'} {module_name} "
                    f"nastala chyba typu {ex}. Tato položka bude přeskočena!"
                )

        return processed

    def _translate_url(self, name: Module, is_install: bool) -> str:
        match name:
            case Module.EDITOR:
                return EDITOR_DOWNLOAD_URL
            case Module.DTMCR:
                return DTMCR_FULL_DOWNLOAD_URL if is_install else DTMCR_PARTIAL_DOWNLOAD_URL
            case Module.THREED:
                return D3_FULL_DOWNLOAD_URL if is_install else D3_PARTIAL_DOWNLOAD_URL
            case Module.IG:
                return IG_FULL_DOWNLOAD_URL if is_install else IG_PARTIAL_DOWNLOAD_URL
            case Module.DWG:
                return DWG_DONWLOAD_URL
            case _:
                raise ValueError(f"Unsupported program: {name}")

    def _download_from_url(self, name: Module, is_install: bool) -> None:
        resp = self._session.get(self._translate_url(name, is_install), stream=True)

        total_size = int(resp.headers.get("content-length", 0))
        block_size = 1024

        with open(f"C:\\{name.value}.zip", "wb") as file, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            desc=f"Probíhá stahování {name.value}",
            file=sys.stdout,
        ) as progress_bar:
            for chunk in resp.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        print(f"Stahování {name.value} dokončeno!")

    def _unzip_file(self, old: str, new: str, name: str) -> None:
        print(f"Probíhá extrahování souboru {name}.zip")
        with ZipFile(old, "r") as zip_ref:
            zip_ref.extractall(new)
        print(f"Extrahování souboru {name}.zip dokončeno")
        remove(old)

    def _run_program(self, exe_path: str) -> None:
        run([
            "powershell",
            "Start-Process",
            exe_path,
            "-Verb",
            "runAs",
            "-Wait",
        ])
        if path.isdir("C:\\V6-INSTALL"):
            rmtree("C:\\V6-INSTALL")