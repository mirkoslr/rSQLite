#!/usr/bin/env bash

set -e

# ==========================================
# rSQLite Node Installer
# ==========================================

# ------------------------------------------
# Configuration
# ------------------------------------------

RSQ_DIR="/opt/rsqlite"
VENV_DIR="$RSQ_DIR/venv"

ETC_DIR="/etc/rsqlite"
DATA_DIR="/var/lib/rsqlite"

DATABASE="$DATA_DIR/rsqlite.db"

RSQ_USER="rsqlite"
RSQ_GROUP="rsqlite"

CLIENT_USER="${SUDO_USER:-$USER}"
CLIENT_HOME="$(getent passwd "$CLIENT_USER" | cut -d: -f6)"

CLIENT_CONFIG_DIR="$CLIENT_HOME/.config/rsqlite"
CLIENT_IDENTITY="$CLIENT_HOME/.reticulum/identities/rsqlite"

SERVER_IDENTITY="$DATA_DIR/.reticulum/identities/rsqlite-server"

SERVER_NAME=""
CLIENT_IDENTITY_HASH=""
SERVER_IDENTITY_HASH=""
SERVER_DESTINATION_HASH=""


# ------------------------------------------
# Functions
# ------------------------------------------

require_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "Error: this installer must be run as root."
        echo "Use: sudo ./install.sh"
        exit 1
    fi
}


show_banner() {
    echo
    echo "=============================="
    echo "       rSQLite Installer"
    echo "=============================="
    echo
}


choose_role() {
    echo "Select node role:"
    echo
    echo "1) Client"
    echo "2) Server"
    echo "3) Client + Server"
    echo "4) Exit"
    echo

    read -rp "Select an option: " choice

    case "$choice" in
        1)
            ROLE="client"
            ;;
        2)
            ROLE="server"
            ;;
        3)
            ROLE="both"
            ;;
        4)
            echo "Installation cancelled."
            exit 0
            ;;
        *)
            echo "Invalid selection."
            exit 1
            ;;
    esac
}


choose_install_mode() {
    echo
    echo "Installation mode:"
    echo
    echo "1) Default"
    echo "2) Custom"
    echo "3) Back"
    echo

    read -rp "Select an option: " choice

    case "$choice" in
        1)
            INSTALL_MODE="default"
            ;;
        2)
            INSTALL_MODE="custom"
            ;;
        3)
            return 1
            ;;
        *)
            echo "Invalid selection."
            return 1
            ;;
    esac
}


prompt_path() {
    local prompt="$1"
    local default="$2"
    local value

    read -rp "$prompt [$default]: " value

    if [ -z "$value" ]; then
        echo "$default"
    else
        echo "$value"
    fi
}


set_default_paths() {
    RSQ_DIR="/opt/rsqlite"
    VENV_DIR="$RSQ_DIR/venv"

    ETC_DIR="/etc/rsqlite"
    DATA_DIR="/var/lib/rsqlite"

    DATABASE="$DATA_DIR/rsqlite.db"

    CLIENT_CONFIG_DIR="$CLIENT_HOME/.config/rsqlite"
    CLIENT_IDENTITY="$CLIENT_HOME/.reticulum/identities/rsqlite"

    SERVER_IDENTITY="$DATA_DIR/.reticulum/identities/rsqlite-server"
}


choose_custom_paths() {
    echo
    echo "Custom installation"
    echo "-------------------"
    echo

    RSQ_DIR=$(prompt_path \
        "Software directory" \
        "/opt/rsqlite")

    VENV_DIR="$RSQ_DIR/venv"

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        ETC_DIR=$(prompt_path \
            "Configuration directory" \
            "/etc/rsqlite")

        DATA_DIR=$(prompt_path \
            "Data directory" \
            "/var/lib/rsqlite")
    fi

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        CLIENT_CONFIG_DIR=$(prompt_path \
            "Client configuration directory" \
            "$CLIENT_HOME/.config/rsqlite")
    fi

    SERVER_IDENTITY="$DATA_DIR/.reticulum/identities/rsqlite-server"
    DATABASE="$DATA_DIR/rsqlite.db"

    echo
}


choose_database() {
    local database_name

    echo
    echo "Database setup"
    echo "--------------"
    echo
    echo "The database will be created automatically by SQLite"
    echo "when the server starts, if it does not already exist."
    echo
    echo "Database directory:"
    echo "  $DATA_DIR"
    echo

    database_name=$(prompt_path \
        "Database file" \
        "rsqlite.db")

    if [[ "$database_name" == */* ]]; then
        echo
        echo "Error: database file name must not contain '/'."
        exit 1
    fi

    if [ -z "$database_name" ]; then
        echo
        echo "Error: database file name cannot be empty."
        exit 1
    fi

    DATABASE="$DATA_DIR/$database_name"

    echo
    echo "Database:"
    echo "  $DATABASE"
    echo
    echo "SQLite will create this file automatically when"
    echo "the server opens the database for the first time."
}


choose_server_name() {
    SERVER_NAME=$(prompt_path \
        "Server name" \
        "$(hostname)")
}


create_directories() {
    echo
    echo "Creating directories..."

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        mkdir -p "$CLIENT_CONFIG_DIR"
        mkdir -p "$(dirname "$CLIENT_IDENTITY")"

        chown "$CLIENT_USER:$CLIENT_USER" \
            "$CLIENT_CONFIG_DIR"

        chown "$CLIENT_USER:$CLIENT_USER" \
            "$CLIENT_HOME/.reticulum"
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        mkdir -p "$ETC_DIR"
        mkdir -p "$DATA_DIR"
    fi
}


create_venv() {
    echo
    echo "Creating Python virtual environment..."

    mkdir -p "$RSQ_DIR"

    python3 -m venv "$VENV_DIR"

    echo
    echo "Installing rSQLite..."

    "$VENV_DIR/bin/python" -m pip install .
}


install_client_config() {
    echo
    echo "Installing client configuration..."

    cp "examples/rsqlite-cli.conf.example" \
       "$CLIENT_CONFIG_DIR/rsqlite-cli.conf"

    chown "$CLIENT_USER:$CLIENT_USER" \
        "$CLIENT_CONFIG_DIR/rsqlite-cli.conf"
}


create_client_identity() {
    echo
    echo "Creating client Reticulum Identity..."

    sudo -u "$CLIENT_USER" \
        "$VENV_DIR/bin/python" -c "
from rsqlite.identity import prepare_identity
prepare_identity('$CLIENT_IDENTITY')
"

    chown -R "$CLIENT_USER:$CLIENT_USER" \
        "$CLIENT_HOME/.reticulum"

    CLIENT_IDENTITY_HASH=$(
        sudo -u "$CLIENT_USER" \
        "$VENV_DIR/bin/python" -c "
import RNS

identity = RNS.Identity.from_file('$CLIENT_IDENTITY')
print(identity.hash.hex())
"
    )

    echo
    echo "Client Identity:"
    echo "  $CLIENT_IDENTITY"

    echo
    echo "Client Identity Hash:"
    echo "  $CLIENT_IDENTITY_HASH"
}


configure_client_identity() {
    local config_file="$CLIENT_CONFIG_DIR/rsqlite-cli.conf"

    echo
    echo "Configuring client Identity..."

    sed -i \
        -e "s|^file = .*|file = $CLIENT_IDENTITY|" \
        "$config_file"

    chown "$CLIENT_USER:$CLIENT_USER" \
        "$config_file"
}


configure_client_path() {
    local profile="$CLIENT_HOME/.profile"
    local path_line="export PATH=\"$VENV_DIR/bin:\$PATH\""

    echo
    echo "Configuring user environment..."

    touch "$profile"

    chown "$CLIENT_USER:$CLIENT_USER" \
        "$profile"

    if ! grep -Fqx "$path_line" "$profile"; then
        printf '\n%s\n' "$path_line" >> "$profile"
    fi

    echo "Added to PATH:"
    echo "  $VENV_DIR/bin"
}


install_server_config() {
    echo
    echo "Installing server configuration..."

    cp "examples/rsqlite-server.conf.example" \
       "$ETC_DIR/rsqlite-server.conf"

    sed -i \
        -e "s|^identity = .*|identity = $SERVER_IDENTITY|" \
        -e "s|^database = .*|database = $DATABASE|" \
        -e "s|^allowed_identities = .*|allowed_identities = $ETC_DIR/allowed_identities|" \
        "$ETC_DIR/rsqlite-server.conf"
}


install_allowed_identities() {
    echo
    echo "Installing allowed identities file..."

    cp "examples/allowed_identities.example" \
       "$ETC_DIR/allowed_identities"
}


create_service_user() {
    echo
    echo "Creating rSQLite service user..."

    if id "$RSQ_USER" >/dev/null 2>&1; then
        echo "User '$RSQ_USER' already exists."
        return
    fi

    useradd \
        --system \
        --home-dir "$DATA_DIR" \
        --shell /usr/sbin/nologin \
        "$RSQ_USER"
}


create_server_identity() {
    echo
    echo "Creating server Reticulum Identity..."

    "$VENV_DIR/bin/python" -c "
from rsqlite.identity import prepare_identity
prepare_identity('$SERVER_IDENTITY')
"

    chown -R "$RSQ_USER:$RSQ_GROUP" \
        "$DATA_DIR/.reticulum"

    SERVER_IDENTITY_HASH=$(
        "$VENV_DIR/bin/python" -c "
import RNS

identity = RNS.Identity.from_file('$SERVER_IDENTITY')
print(identity.hash.hex())
"
    )

    echo
    echo "Server Identity:"
    echo "  $SERVER_IDENTITY"

    echo
    echo "Server Identity Hash:"
    echo "  $SERVER_IDENTITY_HASH"
}


configure_server_destination() {
    echo
    echo "Configuring server Destination..."

    SERVER_DESTINATION_HASH=$(
        "$VENV_DIR/bin/python" -c "
import RNS
from rsqlite.constants import APP_NAME, SERVICE_NAME

identity = RNS.Identity.from_file('$SERVER_IDENTITY')

destination_hash = RNS.Destination.hash_from_name_and_identity(
    f\"{APP_NAME}.{SERVICE_NAME}\",
    identity
)

print(destination_hash.hex())
"
    )

    echo
    echo "Server Destination Hash:"
    echo "  $SERVER_DESTINATION_HASH"
}


configure_local_client_server() {
    local config_file="$CLIENT_CONFIG_DIR/rsqlite-cli.conf"

    echo
    echo "Configuring local server in client configuration..."

    cat >> "$config_file" <<EOF

[server.local]
name = $SERVER_NAME
destination_hash = $SERVER_DESTINATION_HASH
EOF

    chown "$CLIENT_USER:$CLIENT_USER" \
        "$config_file"
}


add_client_identity_to_acl() {
    echo
    echo "Authorizing local client..."

    if ! grep -Fqx "$CLIENT_IDENTITY_HASH" \
        "$ETC_DIR/allowed_identities"; then

        echo "$CLIENT_IDENTITY_HASH" \
            >> "$ETC_DIR/allowed_identities"
    fi

    echo
    echo "Authorized client Identity:"
    echo "  $CLIENT_IDENTITY_HASH"
}


set_server_ownership() {
    echo
    echo "Setting server directory ownership..."

    chown -R "$RSQ_USER:$RSQ_GROUP" "$DATA_DIR"
}


install_systemd_service() {
    echo
    echo "Installing systemd service..."

    cat > /etc/systemd/system/rsqlite-server.service <<EOF
[Unit]
Description=rSQLite Server
After=rnsd.service
Requires=rnsd.service

[Service]
Type=simple
User=$RSQ_USER
ExecStart=$VENV_DIR/bin/python -m rsqlite.server -c $ETC_DIR/rsqlite-server.conf
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload

    systemctl enable rsqlite-server.service

    systemctl start rsqlite-server.service
}


show_final_report() {

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        REPORT_FILE="$DATA_DIR/installation-report.txt"
    else
        REPORT_FILE="$CLIENT_CONFIG_DIR/installation-report.txt"
    fi

    {
        echo
        echo "============================================================"
        echo "rSQLite installation report"
        echo "============================================================"
        echo
        echo "Installation mode: $ROLE"
        echo

        echo "Installation"
        echo "------------"
        echo "Software directory : $RSQ_DIR"
        echo "Virtual environment: $VENV_DIR"
        echo

        if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
            echo "Client"
            echo "------"
            echo "Configuration      : $CLIENT_CONFIG_DIR/rsqlite-cli.conf"
            echo "Identity           : $CLIENT_IDENTITY"
            echo "Identity Hash      : $CLIENT_IDENTITY_HASH"
            echo
            echo "Environment"
            echo "-----------"
            echo "PATH entry         : $VENV_DIR/bin"
            echo
        fi

        if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
            echo "Server"
            echo "------"
            echo "Configuration      : $ETC_DIR/rsqlite-server.conf"
            echo "Identity           : $SERVER_IDENTITY"
            echo "Identity Hash      : $SERVER_IDENTITY_HASH"
            echo "Destination Hash   : $SERVER_DESTINATION_HASH"
            echo

            echo "Database"
            echo "--------"
            echo "Database file      : $DATABASE"
            echo "Database status    :"
            if [ -f "$DATABASE" ]; then
                echo "  Created"
            else
                echo "  Will be created automatically on first SQL request"
            fi
            echo

            echo "Access Control"
            echo "--------------"
            echo "Allowed identities : $ETC_DIR/allowed_identities"
            echo

            echo "Service"
            echo "-------"
            echo "Systemd service    : /etc/systemd/system/rsqlite-server.service"
            echo "Service user       : $RSQ_USER"

            if systemctl is-active --quiet rsqlite-server.service; then
                echo "Status             : active (running)"
            else
                echo "Status             : not running"
            fi

            echo
        fi

        echo "============================================================"
        echo "Installation completed successfully."
        echo
        echo "Installation report saved to:"
        echo "$REPORT_FILE"
        echo "============================================================"

    } | tee "$REPORT_FILE"

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        chown "$RSQ_USER:$RSQ_GROUP" "$REPORT_FILE"
        chmod 0640 "$REPORT_FILE"
    else
        chown "$CLIENT_USER:$CLIENT_USER" "$REPORT_FILE"
        chmod 0644 "$REPORT_FILE"
    fi
}


# ------------------------------------------
# Main
# ------------------------------------------

main() {
    require_root
    show_banner

    while true; do
        choose_role

        echo
        echo "Selected role: $ROLE"
        echo

        if choose_install_mode; then
            break
        fi
    done

    set_default_paths

    if [ "$INSTALL_MODE" = "custom" ]; then
        choose_custom_paths
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        choose_database
    fi

    if [ "$ROLE" = "both" ]; then
        echo
        choose_server_name
    fi

    echo
    echo "Installation mode: $INSTALL_MODE"
    echo "Software directory: $RSQ_DIR"

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        echo "Configuration directory: $ETC_DIR"
        echo "Data directory: $DATA_DIR"
        echo "Database: $DATABASE"
    fi

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        echo "Client configuration: $CLIENT_CONFIG_DIR"
        echo "Client Identity: $CLIENT_IDENTITY"
    fi

    echo

    create_directories
    create_venv

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        install_client_config
        create_client_identity
        configure_client_identity
        configure_client_path
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        create_service_user
        create_server_identity
        configure_server_destination
        install_server_config
        install_allowed_identities
    fi

    if [ "$ROLE" = "both" ]; then
        configure_local_client_server
        add_client_identity_to_acl
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        set_server_ownership
        install_systemd_service
    fi

    show_final_report
}


main
