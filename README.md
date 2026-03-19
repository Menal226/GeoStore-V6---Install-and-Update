# GeoStore V6 - Install and Update
Tato aplikace slouží jako nástroj pro snadnou instalaci a aktualizaci softwaru [GeoStore V6](https://www.geovap.com/cs/geostore-v6). Jelikož byl tento nástroj vytvořen na zakázku, je aktuálně konfigurován pro stahování konkrétních aplikačních modulů (s možností budoucího rozšíření).

## Instalace
Nejnovější verzi ve formátu `.exe` stáhněte v sekci [releases](https://github.com/Menal226/GeoStore-V6---Install-and-Update/releases) a následně ji spusťte. 

Vzhledem k absenci placeného digitálního podpisu se může při spuštění zobrazit varování systému Windows (Microsoft Defender SmartScreen). V takovém případě postupujte podle následujících instrukcí:

![warning1](https://github.com/user-attachments/assets/cb4a6a46-db94-4f45-b2bb-425ba817896a) 
![warning2](https://github.com/user-attachments/assets/b0a038ba-735b-4fd1-8448-06c8b7e09701)

## Návod k použití
Aplikaci je nutné spustit v **režimu administrátora**, který je vyžadován pro instalaci jednotlivých modulů. 

1. **Přihlášení:** Po spuštění zadejte své přihlašovací údaje do [systému technické podpory](http://portal.geostore.cz/v6/support/). Tento krok lze automatizovat pomocí [přepínačů programu](#přepínače-programu).
2. **Výběr modulů:** Pomocí příslušných kláves vyberte moduly, které si přejete instalovat či aktualizovat. 
3. **Potvrzení:** Výběr potvrďte dvojitým stisknutím klávesy **ENTER**. 
4. **Dokončení:** Po automatickém stažení modulů je nutné dokončit instalaci manuálním potvrzením v samotném softwaru společnosti Geovap.

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
