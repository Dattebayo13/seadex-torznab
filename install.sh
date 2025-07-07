#!/bin/bash

REPO="Dattebayo13/seadex-torznab"
SERVICE_NAME="seadex-torznab"
SYSTEMD_PATH="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_PATH/$SERVICE_NAME.service"
VENV_DIR="$HOME/.seadex-torznab-venv"

function uninstall() {
  echo "Uninstalling $SERVICE_NAME..."
  systemctl --user stop $SERVICE_NAME 2>/dev/null
  systemctl --user disable $SERVICE_NAME 2>/dev/null
  rm -f "$SERVICE_FILE"
  systemctl --user daemon-reload
  if [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
    echo "Removed virtual environment."
  fi
  echo "Uninstalled."
  exit 0
}

# Prompt the user for install or uninstall
echo "What would you like to do?"
select choice in "Install" "Uninstall" "Exit"; do
  case $choice in
    Install ) break ;;
    Uninstall ) uninstall ;;
    Exit ) echo "Exiting."; exit 0 ;;
    * ) echo "Invalid choice. Please enter 1, 2, or 3." ;;
  esac
done

echo "Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install --upgrade "git+https://github.com/$REPO.git"

echo "Installed seadex-torznab Python package in virtual environment."

read -p "Create and enable systemd user service (run on login)? [Y/N] " enable_service
if [[ "$enable_service" =~ ^[Yy]$ ]]; then
  mkdir -p "$SYSTEMD_PATH"
  cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Seadex Torznab Proxy (Python)
After=network.target

[Service]
ExecStart=$VENV_DIR/bin/seadex-torznab
Restart=on-failure

[Install]
WantedBy=default.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now $SERVICE_NAME
  echo "Service '$SERVICE_NAME' started and enabled (user systemd). Running on Port 49152."
else
  echo "You can run it manually with:"
  echo "  source $VENV_DIR/bin/activate && seadex-torznab"
fi

echo "Done."
