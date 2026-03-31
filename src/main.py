from gui.geostore_window import GeoStoreWindow
from startup.admin import ensure_admin_on_start


def main():
    ensure_admin_on_start()
    app = GeoStoreWindow()
    app.mainloop()


if __name__ == "__main__":
    main()