import flama


def main():
    flama.run(flama_app="src.api.app:app", server_host="0.0.0.0", server_port=8000, server_reload=True)


if __name__ == "__main__":
    main()
