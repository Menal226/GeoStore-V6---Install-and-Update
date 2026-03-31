from window import GeoStoreWindow, ensure_admin_on_start


def main():
    ensure_admin_on_start()
    app = GeoStoreWindow()
    app.mainloop()


if __name__ == "__main__":
    main()