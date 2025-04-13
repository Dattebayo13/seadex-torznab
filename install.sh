#!/bin/bash

REPO="Dattebayo13/seadex-torznab"
INSTALL_DIR="$HOME/.local/bin"
SERVICE_NAME="seadex-torznab"
ZIP_NAME="seadex-torznab-linux-binary.zip"
BINARY_NAME="seadex-torznab"
SYSTEMD_PATH="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_PATH/$SERVICE_NAME.service"

function uninstall() {
  echo "Uninstalling $SERVICE_NAME..."
  systemctl --user stop $SERVICE_NAME 2>/dev/null
  systemctl --user disable $SERVICE_NAME 2>/dev/null
  rm -f "$INSTALL_DIR/$SERVICE_NAME"
  rm -f "$SERVICE_FILE"
  systemctl --user daemon-reload
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

echo "Fetching latest release..."
latest_url=$(curl -s "https://api.github.com/repos/$REPO/releases" \
  | jq -r '.[0].assets[] | select(.name == "seadex-torznab-linux-binary.zip") | .browser_download_url')

if [ -z "$latest_url" ]; then
  echo "Could not find latest release zip. Check your repo or rename the asset."
  exit 1
fi

mkdir -p "$INSTALL_DIR"
mkdir -p "$SYSTEMD_PATH"
tmp_dir=$(mktemp -d)

echo "Downloading $ZIP_NAME..."
curl -L "$latest_url" -o "$tmp_dir/$ZIP_NAME"

echo "Extracting..."
unzip -o "$tmp_dir/$ZIP_NAME" -d "$tmp_dir"

if [ ! -f "$tmp_dir/$BINARY_NAME" ]; then
  echo "Binary '$BINARY_NAME' not found in zip."
  exit 1
fi

echo "Installing to $INSTALL_DIR..."
mv "$tmp_dir/$BINARY_NAME" "$INSTALL_DIR/$SERVICE_NAME"
chmod +x "$INSTALL_DIR/$SERVICE_NAME"
rm -rf "$tmp_dir"

echo "Installed: $INSTALL_DIR/$SERVICE_NAME"

read -p "Create and enable systemd user service (run on login)? [Y/N] " enable_service
if [[ "$enable_service" =~ ^[Yy]$ ]]; then
  cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Seadex Torznab Proxy
After=network.target

[Service]
ExecStart=$INSTALL_DIR/$SERVICE_NAME
Restart=on-failure

[Install]
WantedBy=default.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable --now $SERVICE_NAME
  echo "Service '$SERVICE_NAME' started and enabled (user systemd). Running on Port 49152"
else
  echo "You can run it manually with:"
  echo "  $INSTALL_DIR/$SERVICE_NAME"
fi

echo "Done."
