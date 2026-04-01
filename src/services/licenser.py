from requests import Session
from resources.urls import LICENSE_URL
from pathlib import Path

class Licenser:
    def __init__(self, session: Session):
        self._session = session

    def _get_license_string(self) -> str:
        payload = {
            "action" : "mobile.review",
            "user_seat": "",
            "user_role": "licuser",
            "folder_id": "dataNode02",
            "parameters": [
                {
                    "name": "page",
                    "type": "N",
                    "value": 1    
                },
                {
                    "name": "filter",
                    "value": "null"
                }
            ]
        }
        try:
            resp = self._session.post(LICENSE_URL, json=payload)
        except Exception:
            print("Během stahování licence nastala chyba při komunikaci se servery Geostore.")
            return ""

        if resp.status_code != 200:
            print("Během stahování licence nastala chyba při komunikaci se servery Geostore.")
            return ""
        
        try:
            resp_json = resp.json()
        except Exception:
            print("Během stahování licence nastala chyba při komunikaci se servery Geostore.")
            return ""

        if resp_json.get("state") != 1:
            print("Během stahování licence nastala chyba při komunikaci se servery Geostore.")
            return ""
    
        try:
            return resp_json.get("table", {}).get("data", {}).get("rows", [])[0][4]
        except Exception:
            return ""

    def add_license_to_instalation(self):
        license = self._get_license_string()
        if not license:
            return
        license_path = Path(r"C:\Program Files\GEOVAP\GeoStoreV6")
        license_path.mkdir(parents=True, exist_ok=True)
        with open(license_path / "gsfl.lic", "w") as file:
            file.write(license)
