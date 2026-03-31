from requests import Session
from enums.module import Module
from resources.urls import GEOSTORE_URL
from datetime import datetime
from pathlib import Path
from os import getenv
import json

class Checker:
    def __init__(self, session: Session):
        self._session = session
        self._save_path =  Path(getenv("APPDATA")) / "GeoStore Updater" / "save_times"
    
    def _name_to_payload(self, name: Module) -> dict[str, str]:
        match name:
            case Module.EDITOR | Module.DTMCR:
                arg1, arg2 = "fldFilesDTMCR", "DTM"
            case Module.DWG:
                arg1, arg2 = "fldFilesDMVS", "DWG"
            case Module.IG:
                arg1, arg2 = "fldFilesIG", "IG"
            case Module.THREED:
                arg1, arg2 = "fldFilesLAS", "LAS"
        return {
            "action": "mobile.review",
            "user_seat": "",
            "user_role": arg2,
            "folder_id": arg1,
            "parameters": [
                {"name": "page", "type": "N", "value": 1},
                {"name": "filter", "value": None}
            ]
        }
    
    def _process_response(self, response: dict, name: Module) -> datetime:
        match name:
            case Module.EDITOR:
                file = "zakladni_graficky_editor_GSV6_x64.zip"
            case Module.DTMCR:
                file = "castecna_instalace_aplikace_DTMCR.zip"
            case Module.DWG:
                file = "instalace_rozš&#237;řen&#237;_GSV6_DWG_DGN_x64.zip"
            case Module.IG:
                file = "castecna_instalace_aplikace_IG.zip"
            case Module.THREED:
                file = "castecna_instalace_aplikace_3D.zip"

        data = response.get("table", {}).get("data", {}).get("rows", [])
        for possible in data:
            if possible[3] == file:
                return datetime.strptime(possible[4], "%d.%m.%Y")
        return datetime.fromtimestamp(0)
    
    def get_newest_update_time(self, name: Module) -> datetime:
        resp = self._session.post(GEOSTORE_URL, json=self._name_to_payload(name))
        if resp.status_code != 200:
            print(f"Nepodařilo se získat informaci o datu nejnovější verze {name}")
            return datetime.fromtimestamp(0)

        resp_json = resp.json()
        if resp_json["state"] != 1:
            print(f"Nepodařilo se získat informaci o datu nejnovější verze {name}")
            return datetime.fromtimestamp(0)

        return self._process_response(resp_json, name)
    
    def _get_latest_update_times(self) -> dict[Module, datetime]:
        return {
            Module.EDITOR: self.get_newest_update_time(Module.EDITOR),
            Module.DTMCR: self.get_newest_update_time(Module.DTMCR),
            Module.DWG: self.get_newest_update_time(Module.DWG),
            Module.IG: self.get_newest_update_time(Module.IG),
            Module.THREED: self.get_newest_update_time(Module.THREED),
        }

    def _get_saved_version_times(self) -> dict[Module, datetime]:
        if not self._save_path.exists():
            return {}

        with open(self._save_path, "r") as file:
            try:
                raw_data = json.load(file)
            except json.JSONDecodeError:
                return {}

        parsed = {}
        for key, value in raw_data.items():
            parsed[Module(key)] = datetime.fromisoformat(value)
        
        return parsed

    def _save_version_times(self, save_times: dict[Module, datetime]):
        self._save_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {
            module.value: dt.isoformat() for module, dt in save_times.items()
        }
        with open(self._save_path, "w") as file:
            json.dump(serializable, file)

    def update_last_saved_time(self, module: Module, date: datetime):
        times = self._get_saved_version_times()
        times[module] = date
        self._save_version_times(times)

    '''
    Returns a dictionary where each value coresponds to if the modules has a newer version available
    If there has been an error in trying to find the newest version the value is None
    '''
    def get_update_status(self) -> dict[Module, bool | None]:
        online = self._get_latest_update_times()
        offline = self._get_saved_version_times()
        failed = datetime.fromtimestamp(0)

        statuses: dict[Module, bool | None] = {}
        for key, online_time in online.items():
            if online_time == failed:
                statuses[key] = None
                continue
            statuses[key] = online_time != offline.get(key, failed)
        return statuses
