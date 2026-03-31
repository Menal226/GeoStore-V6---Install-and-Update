import json
from datetime import datetime
from os import getenv
from pathlib import Path

from requests import Session

from enums.module import Module, get_module_config, get_module_order
from resources.urls import GEOSTORE_URL


class Checker:
    def __init__(self, session: Session):
        self._session = session
        self._save_path = Path(getenv("APPDATA")) / "GeoStore Updater" / "save_times"

    def _name_to_payload(self, name: Module) -> dict[str, str]:
        config = get_module_config(name)
        return {
            "action": "mobile.review",
            "user_seat": "",
            "user_role": config.checker_user_role,
            "folder_id": config.checker_folder_id,
            "parameters": [{"name": "page", "type": "N", "value": 1}, {"name": "filter", "value": None}],
        }

    def _process_response(self, response: dict, name: Module) -> datetime:
        expected_file_name = get_module_config(name).checker_file_name

        data = response.get("table", {}).get("data", {}).get("rows", [])
        for possible in data:
            if possible[3] == expected_file_name:
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
        return {module: self.get_newest_update_time(module) for module in get_module_order()}

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
            try:
                parsed[Module(key)] = datetime.fromisoformat(value)
            except (TypeError, ValueError):
                # Ignore stale/invalid saved entries from previous app versions.
                continue

        return parsed

    def _save_version_times(self, save_times: dict[Module, datetime]):
        self._save_path.parent.mkdir(parents=True, exist_ok=True)
        serializable = {module.value: dt.isoformat() for module, dt in save_times.items()}
        with open(self._save_path, "w") as file:
            json.dump(serializable, file)

    def update_last_saved_time(self, module: Module, date: datetime):
        times = self._get_saved_version_times()
        times[module] = date
        self._save_version_times(times)

    """
    Returns a dictionary where each value coresponds to if the modules has a newer version available.
    If there has been an error in trying to find the newest version the value is None.
    """

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