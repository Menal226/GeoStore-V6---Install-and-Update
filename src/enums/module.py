from dataclasses import dataclass
from enum import Enum

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

class Module(Enum):
    EDITOR = "Editor"
    DTMCR = "DTMCR"
    THREED = "3D"
    IG = "IG"
    DWG = "DWG"


@dataclass(frozen=True)
class ModuleConfig:
    display_name: str
    selection_key: str
    checker_folder_id: str
    checker_user_role: str
    checker_file_name: str
    install_download_url: str
    update_download_url: str | None = None
    installer_executable: str = "Install.exe"
    post_install_executables: tuple[str, ...] = ()

    def get_download_url(self, is_install: bool) -> str:
        if is_install:
            return self.install_download_url
        return self.update_download_url or self.install_download_url


MODULE_CONFIGS: dict[Module, ModuleConfig] = {
    Module.EDITOR: ModuleConfig(
        display_name="Základní Grafický Editor",
        selection_key="1",
        checker_folder_id="fldFilesDTMCR",
        checker_user_role="DTM",
        checker_file_name="zakladni_graficky_editor_GSV6_x64.zip",
        install_download_url=EDITOR_DOWNLOAD_URL,
        installer_executable="setup.exe",
        post_install_executables=(
            r"C:\Program Files\GEOVAP\GeoStoreV6\Redist\vc2010redist_x64.exe",
            r"C:\Program Files\GEOVAP\GeoStoreV6\Redist\vc2012redist_x64.exe",
        ),
    ),
    Module.DTMCR: ModuleConfig(
        display_name="Aplikace DTMCR",
        selection_key="2",
        checker_folder_id="fldFilesDTMCR",
        checker_user_role="DTM",
        checker_file_name="castecna_instalace_aplikace_DTMCR.zip",
        install_download_url=DTMCR_FULL_DOWNLOAD_URL,
        update_download_url=DTMCR_PARTIAL_DOWNLOAD_URL,
    ),
    Module.IG: ModuleConfig(
        display_name="Aplikace IG",
        selection_key="3",
        checker_folder_id="fldFilesIG",
        checker_user_role="IG",
        checker_file_name="castecna_instalace_aplikace_IG.zip",
        install_download_url=IG_FULL_DOWNLOAD_URL,
        update_download_url=IG_PARTIAL_DOWNLOAD_URL,
    ),
    Module.THREED: ModuleConfig(
        display_name="Aplikace 3D",
        selection_key="4",
        checker_folder_id="fldFilesLAS",
        checker_user_role="LAS",
        checker_file_name="castecna_instalace_aplikace_3D.zip",
        install_download_url=D3_FULL_DOWNLOAD_URL,
        update_download_url=D3_PARTIAL_DOWNLOAD_URL,
    ),
    Module.DWG: ModuleConfig(
        display_name="Aplikace DWG",
        selection_key="5",
        checker_folder_id="fldFilesDMVS",
        checker_user_role="DWG",
        checker_file_name="instalace_rozš&#237;řen&#237;_GSV6_DWG_DGN_x64.zip",
        install_download_url=DWG_DONWLOAD_URL,
    ),
}

MODULE_ORDER = tuple(MODULE_CONFIGS.keys())
MODULE_BY_SELECTION_KEY = {
    cfg.selection_key: module for module, cfg in MODULE_CONFIGS.items()
}


def get_module_config(module: Module) -> ModuleConfig:
    return MODULE_CONFIGS[module]


def get_module_order() -> tuple[Module, ...]:
    return MODULE_ORDER


def get_module_from_selection_key(selection_key: str) -> Module | None:
    return MODULE_BY_SELECTION_KEY.get(selection_key)


def _validate_module_configs() -> None:
    configured = set(MODULE_CONFIGS.keys())
    available = set(Module)

    if configured != available:
        missing = ", ".join(sorted(module.value for module in available - configured))
        extra = ", ".join(sorted(module.value for module in configured - available))
        raise ValueError(f"Module configuration mismatch. Missing: [{missing}] Extra: [{extra}]")

    if len(MODULE_BY_SELECTION_KEY) != len(MODULE_CONFIGS):
        raise ValueError("Duplicate selection keys in module configuration")


_validate_module_configs()
