from os import system
from requests import Session
from urls import GEOSTORE_URL


class Authenticator:
    def __init__(self, session: Session):
        self._session = session

    def login(self, user_name: str, password: str) -> None:
        while True:
            if user_name == "":
                current_user = input("Zadejte uživatelské jméno: ")
            else:
                current_user = user_name
                print(f"Uživatelské jméno z přepínače: {user_name}")
            
            if password == "":
                current_password = input("Zadejte heslo: ")
            else:
                current_password = password
                print(f"Heslo z přepínače: {password}")

            payload = {
                "action": "mobile.authentication",
                "parameters": [
                    {"name": "action", "value": "mobile.authentication"},
                    {"name": "identifier", "value": ""},
                    {"name": "user_name", "value": current_user},
                    {"name": "user_password", "value": current_password},
                ],
            }

            resp = self._session.post(GEOSTORE_URL, json=payload)

            if resp.status_code != 200:
                system("cls")
                print(
                    "\033[31mNastala chyba při komunikaci se servery GeoStore, zkontrolujte připojení k Internetu a zkuste znovu.\033[0m"
                )
                user_name = ""
                password = ""
                continue

            if resp.json()["state"] != 0:
                system("cls")
                print("\033[31mZadané uživatelské jméno nebo heslo není správné.\033[0m")
                user_name = ""
                password = ""
                continue

            return
