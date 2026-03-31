# GeoStore V6 - Install and Update
Tato aplikace slouží jako nástroj pro snadnou instalaci a aktualizaci softwaru [GeoStore V6](https://www.geovap.com/cs/geostore-v6). Jelikož byl tento nástroj vytvořen na zakázku, je aktuálně konfigurován pro stahování konkrétních aplikačních modulů (s možností budoucího rozšíření).

## Instalace
Nejnovější verzi ve formátu `.exe` stáhněte v sekci [releases](https://github.com/Menal226/GeoStore-V6---Install-and-Update/releases) a následně ji spusťte. 

Vzhledem k absenci placeného digitálního podpisu se může při spuštění zobrazit varování systému Windows (Microsoft Defender SmartScreen). V takovém případě postupujte podle následujících instrukcí:

![warning1](https://github.com/user-attachments/assets/cb4a6a46-db94-4f45-b2bb-425ba817896a) 
![warning2](https://github.com/user-attachments/assets/b0a038ba-735b-4fd1-8448-06c8b7e09701)

## Návod k použití
Aplikace se při spuštění automaticky pokusí vyžádat režim administrátora, který je nutný pro instalaci a aktualizaci jednotlivých modulů.

1. **Přihlášení:** Po spuštění zadejte své přihlašovací údaje do [systému technické podpory](http://portal.geostore.cz/v6/support/). Tento krok lze automatizovat pomocí [přepínačů programu](#přepínače-programu).

   ![login](https://github.com/user-attachments/assets/565163cd-429a-4108-8cf9-c92cbe6b7da1)

2. **Výběr modulů:** Ze seznamu vyberte moduly, které chcete instalovat nebo aktualizovat.

3. **Potvrzení:** Pomocí příslušného tlačítka potvrďte výběr a spusťte instalaci nebo aktualizaci. Aplikace zobrazí potvrzovací dialog.

   ![select](https://github.com/user-attachments/assets/ec5c933b-54cf-4c19-ab2e-4481f7009574)

4. **Dokončení:** Po automatickém stažení a rozbalení modulů dokončete instalaci v otevřeném instalačním okně.

## Stav modulu
Před přihlášením je u všech modulů zobrazen stav **Vyžaduje přihlášení**.

Po úspěšném přihlášení aplikace porovnává nejnovější dostupnou verzi na serveru s poslední uloženou verzí modulu. Poslední uložená verze se zapisuje po úspěšné aktualizaci modulu v této aplikaci.

- **Nejnovější verze** – neexistuje novější verze modulu.
- **Stará verze** – existuje novější verze modulu, nebo modul ještě nemá uloženou poslední aktualizovanou verzi.
- **Nelze ověřit verzi** – nepodařilo se zjistit nejnovější verzi na serveru (například kvůli chybě připojení nebo neplatné odpovědi serveru).

## Přepínače programu
Pro automatizaci procesů můžete využít následující parametry:
* `-u` (`--jmeno`) `[uživatelské jméno]` – nastaví přihlašovací jméno pro systém podpory.
* `-p` (`--heslo`) `[heslo]` – nastaví heslo pro systém podpory.
* `-s` (`--vyber`) `[číslice]` – definuje moduly, které se mají automaticky vybrat ke zpracování (simuluje stisk kláves).

### Jak přepínače použít?
Nejsnadnější cestou je vytvoření zástupce aplikace:
1. Klikněte pravým tlačítkem na soubor `.exe` a zvolte **Vytvořit zástupce**.
2. Na nově vytvořeného zástupce klikněte pravým tlačítkem a zvolte **Vlastnosti**.
3. V kartě **Zástupce** do pole **Cíl** dopište za uvozovky požadované přepínače (např. `...app.exe -u uzivatel -p heslo123`).
