from requests import Session
from resources.urls import GEOSTORE_URL


class Authenticator:
    def __init__(self, session: Session):
        self._session = session

    def login(self, user_name: str, password: str) -> bool:
        current_user = user_name.strip()
        current_password = password

        if not current_user or not current_password:
            print("Vyplňte uživatelské jméno i heslo.")
            return False

        payload = {
            "action": "mobile.authentication",
            "parameters": [
                {"name": "action", "value": "mobile.authentication"},
                {"name": "identifier", "value": ""},
                {"name": "user_name", "value": current_user},
                {"name": "user_password", "value": current_password},
            ],
        }

        try:
            resp = self._session.post(GEOSTORE_URL, json=payload)
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
