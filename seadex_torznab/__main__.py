from seadex_torznab.app import app
import sys


def main():
    """Run the Flask app with optional port argument."""
    default_port = 49152
    port = default_port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port. Using default port {default_port}.")
    app.run(port=port, debug=True)


if __name__ == "__main__":
    main()
