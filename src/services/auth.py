from requests import Session

from resources.urls import GEOSTORE_URL, LICENSE_URL


class Authenticator:
    def __init__(self, session: Session):
        self._session = session

    def _login_to(self, user_name: str, password: str, url: str) -> bool:

        if not user_name or not password:
            print("Vyplňte uživatelské jméno i heslo.")
            return False

        payload = {
            "action": "mobile.authentication",
            "parameters": [
                {"name": "action", "value": "mobile.authentication"},
                {"name": "identifier", "value": ""},
                {"name": "user_name", "value": user_name},
                {"name": "user_password", "value": password},
            ],
        }

        try:
            resp = self._session.post(url, json=payload)
        except Exception:
            print(
                "Nastala chyba při komunikaci se servery GeoStore, zkontrolujte připojení k Internetu a zkuste znovu."
            )
            return False

        if resp.status_code != 200:
            print(
                "Nastala chyba při komunikaci se servery GeoStore, zkontrolujte připojení k Internetu a zkuste znovu."
            )
            return False

        try:
            resp_json = resp.json()
        except ValueError:
            print("Server vrátil neplatnou odpověď.")
            return False

        if resp_json.get("state") != 0:
            print("Zadané uživatelské jméno nebo heslo není správné.")
            return False

        return True

    def download_server_login(self, user_name: str, password: str) -> bool:
        return self._login_to(user_name, password, GEOSTORE_URL)

    def license_server_login(self, user_name: str, password: str) -> bool:
        return self._login_to(user_name, password, LICENSE_URL)

    def login(self, user_name: str, password: str):
        return self.download_server_login(user_name, password) and \
            self.license_server_login(user_name, password)