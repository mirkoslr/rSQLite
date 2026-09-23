#!/usr/bin/env bash

set -e

# ==========================================
# rSQLite Installer
# User-level installation
# ==========================================

CLIENT_HOME="$HOME"

CONFIG_DIR="$CLIENT_HOME/.config/rsqlite"
DATA_DIR="$CLIENT_HOME/.rsqlite"

CLIENT_CONFIG="$CONFIG_DIR/rsqlite-cli.conf"
SERVER_CONFIG="$CONFIG_DIR/rsqlite-server.conf"
ALLOWED_IDENTITIES="$CONFIG_DIR/allowed_identities"

CLIENT_IDENTITY="$CLIENT_HOME/.reticulum/identities/rsqlite"
SERVER_IDENTITY="$DATA_DIR/identities/rsqlite-server"

DATABASE="$DATA_DIR/rsqlite.db"

SERVER_NAME=""
CLIENT_IDENTITY_HASH=""
SERVER_IDENTITY_HASH=""
SERVER_DESTINATION_HASH=""

ROLE=""
INSTALL_MODE=""


# ==========================================
# General
# ==========================================

show_banner() {
    echo
    echo "=============================="
    echo "       rSQLite Installer"
    echo "=============================="
    echo
}


check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        echo
        echo "Error: rSQLite uses a user-level installation."
        echo
        echo "Do not run this installer with sudo."
        echo
        echo "Use:"
        echo "  ./install.sh"
        echo
        exit 1
    fi
}


require_pipx() {
    if command -v pipx >/dev/null 2>&1; then
        return
    fi

    echo
    echo "Error: pipx is required to install rSQLite."
    echo
    echo "Install pipx using your operating system package manager."
    echo
    echo "On Debian:"
    echo
    echo "  sudo apt install pipx"
    echo
    exit 1
}


# ==========================================
# Selection
# ==========================================

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
            return 0
            ;;
        2)
            INSTALL_MODE="custom"
            return 0
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


prompt_value() {
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


# ==========================================
# Paths
# ==========================================

set_default_paths() {
    CONFIG_DIR="$CLIENT_HOME/.config/rsqlite"
    DATA_DIR="$CLIENT_HOME/.rsqlite"

    CLIENT_CONFIG="$CONFIG_DIR/rsqlite-cli.conf"
    SERVER_CONFIG="$CONFIG_DIR/rsqlite-server.conf"
    ALLOWED_IDENTITIES="$CONFIG_DIR/allowed_identities"

    CLIENT_IDENTITY="$CLIENT_HOME/.reticulum/identities/rsqlite"
    SERVER_IDENTITY="$DATA_DIR/identities/rsqlite-server"

    DATABASE="$DATA_DIR/rsqlite.db"
}


choose_custom_paths() {
    echo
    echo "Custom installation"
    echo "-------------------"
    echo
    echo "All paths must remain inside directories"
    echo "accessible by the current user."
    echo

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        CONFIG_DIR=$(prompt_value \
            "Configuration directory" \
            "$CLIENT_HOME/.config/rsqlite")
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        DATA_DIR=$(prompt_value \
            "Data directory" \
            "$CLIENT_HOME/.rsqlite")
    fi

    CLIENT_CONFIG="$CONFIG_DIR/rsqlite-cli.conf"
    SERVER_CONFIG="$CONFIG_DIR/rsqlite-server.conf"
    ALLOWED_IDENTITIES="$CONFIG_DIR/allowed_identities"

    CLIENT_IDENTITY="$CLIENT_HOME/.reticulum/identities/rsqlite"
    SERVER_IDENTITY="$DATA_DIR/identities/rsqlite-server"

    DATABASE="$DATA_DIR/rsqlite.db"
}


# ==========================================
# Server settings
# ==========================================

choose_database() {
    local database_name

    echo
    echo "Database setup"
    echo "--------------"
    echo

    echo "The database will be created automatically"
    echo "when the server receives its first SQL request."
    echo

    database_name=$(prompt_value "Database file" "rsqlite.db")

    if [ -z "$database_name" ]; then
        echo
        echo "Error: database file name cannot be empty."
        exit 1
    fi

    if [[ "$database_name" == */* ]]; then
        echo
        echo "Error: database file name must not contain '/'."
        exit 1
    fi

    DATABASE="$DATA_DIR/$database_name"

    echo
    echo "Database:"
    echo "  $DATABASE"
}


choose_server_name() {
    SERVER_NAME=$(prompt_value "Server name" "$(hostname)")
}


# ==========================================
# Directories
# ==========================================

create_directories() {
    echo
    echo "Creating directories..."

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        mkdir -p "$CONFIG_DIR"
        mkdir -p "$(dirname "$CLIENT_IDENTITY")"
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        mkdir -p "$CONFIG_DIR"
        mkdir -p "$DATA_DIR"
        mkdir -p "$(dirname "$SERVER_IDENTITY")"
    fi
}


# ==========================================
# pipx / Python
# ==========================================

install_rsqlite() {
    echo
    echo "Installing rSQLite with pipx..."

    pipx install . --force

    echo
    echo "rSQLite installed."
}


pipx_rsqlite_python() {
    local venv_dir
    local python_bin

    venv_dir=$(pipx environment --value PIPX_LOCAL_VENVS)
    python_bin="$venv_dir/rsqlite/bin/python"

    if [ ! -x "$python_bin" ]; then
        echo
        echo "Error: rSQLite Python environment not found:"
        echo "  $python_bin"
        echo
        exit 1
    fi

    "$python_bin" "$@"
}


# ==========================================
# Client
# ==========================================

install_client_config() {
    echo
    echo "Creating client configuration..."

    cat > "$CLIENT_CONFIG" <<EOF
[identity]

file = $CLIENT_IDENTITY
EOF

    chmod 0600 "$CLIENT_CONFIG"
}


create_client_identity() {
    echo
    echo "Creating client Reticulum Identity..."

    pipx_rsqlite_python -c "
from rsqlite.identity import prepare_identity
prepare_identity('$CLIENT_IDENTITY')
"

    CLIENT_IDENTITY_HASH=$(
        pipx_rsqlite_python -c "
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


configure_client_server() {
    local config_file="$CLIENT_CONFIG"

    echo
    echo "Configuring server in client configuration..."

    cat >> "$config_file" <<EOF

[server.local]

name = $SERVER_NAME
destination_hash = $SERVER_DESTINATION_HASH
EOF

    chmod 0600 "$config_file"
}


# ==========================================
# Server
# ==========================================

create_server_identity() {
    echo
    echo "Creating server Reticulum Identity..."

    pipx_rsqlite_python -c "
from rsqlite.identity import prepare_identity
prepare_identity('$SERVER_IDENTITY')
"

    SERVER_IDENTITY_HASH=$(
        pipx_rsqlite_python -c "
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
        pipx_rsqlite_python -c "
import RNS
from rsqlite.constants import APP_NAME, SERVICE_NAME

identity = RNS.Identity.from_file('$SERVER_IDENTITY')

destination_hash = RNS.Destination.hash_from_name_and_identity(
    f'{APP_NAME}.{SERVICE_NAME}',
    identity
)

print(destination_hash.hex())
"
    )

    echo
    echo "Server Destination Hash:"
    echo "  $SERVER_DESTINATION_HASH"
}


install_server_config() {
    echo
    echo "Creating server configuration..."

    cat > "$SERVER_CONFIG" <<EOF
[server]

identity = $SERVER_IDENTITY
database = $DATABASE
allowed_identities = $ALLOWED_IDENTITIES

[announce]

enabled = no
announce_at_start = yes
EOF

    chmod 0600 "$SERVER_CONFIG"
}


install_allowed_identities() {
    echo
    echo "Creating allowed identities file..."

    if [ ! -f "$ALLOWED_IDENTITIES" ]; then
        touch "$ALLOWED_IDENTITIES"
    fi

    chmod 0600 "$ALLOWED_IDENTITIES"
}


add_client_identity_to_acl() {
    echo
    echo "Authorizing local client..."

    if ! grep -Fqx "$CLIENT_IDENTITY_HASH" "$ALLOWED_IDENTITIES"; then
        echo "$CLIENT_IDENTITY_HASH" >> "$ALLOWED_IDENTITIES"
    fi

    echo
    echo "Authorized client Identity:"
    echo "  $CLIENT_IDENTITY_HASH"
}


# ==========================================
# Report
# ==========================================

show_final_report() {
    local report_file

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        report_file="$DATA_DIR/installation-report.txt"
    else
        report_file="$CONFIG_DIR/installation-report.txt"
    fi

    {
        echo
        echo "============================================================"
        echo "rSQLite installation report"
        echo "============================================================"
        echo

        echo "Installation"
        echo "------------"
        echo "Role               : $ROLE"
        echo "Package manager    : pipx"
        echo "Commands           : rsqlite, rsqlite-server"
        echo

        if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
            echo "Client"
            echo "------"
            echo "Configuration      : $CLIENT_CONFIG"
            echo "Identity           : $CLIENT_IDENTITY"
            echo "Identity Hash      : $CLIENT_IDENTITY_HASH"
            echo
        fi

        if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
            echo "Server"
            echo "------"
            echo "Configuration      : $SERVER_CONFIG"
            echo "Identity           : $SERVER_IDENTITY"
            echo "Identity Hash      : $SERVER_IDENTITY_HASH"
            echo "Destination Hash   : $SERVER_DESTINATION_HASH"
            echo

            echo "Database"
            echo "--------"
            echo "Database file      : $DATABASE"

            if [ -f "$DATABASE" ]; then
                echo "Database status    : Created"
            else
                echo "Database status    : Will be created on first SQL request"
            fi

            echo
            echo "Access Control"
            echo "--------------"
            echo "Allowed identities : $ALLOWED_IDENTITIES"
            echo

            echo "Runtime"
            echo "-------"
            echo "Server             : installed, not started"
            echo "systemd service    : not installed"
            echo "rnsd dependency    : none"
        fi

        echo
        echo "Reticulum"
        echo "---------"
        echo "Reticulum is installed as an rSQLite dependency."
        echo "Reticulum CLI tools are not installed by rSQLite."
        echo
        echo "============================================================"
        echo "Installation completed successfully."
        echo
        echo "Start the client with:"
        echo "  rsqlite"

        if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
            echo
            echo "Start the server manually with:"
            echo "  rsqlite-server -c $SERVER_CONFIG"
        fi

        echo
        echo "Installation report:"
        echo "  $report_file"
        echo "============================================================"
    } | tee "$report_file"

    chmod 0600 "$report_file"
}


# ==========================================
# Main
# ==========================================

main() {
    check_not_root
    show_banner
    require_pipx

    while true; do
        choose_role

        echo
        echo "Selected role: $ROLE"

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
    echo

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        echo "Client configuration: $CLIENT_CONFIG"
        echo "Client Identity:      $CLIENT_IDENTITY"
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        echo "Server configuration:  $SERVER_CONFIG"
        echo "Server data:          $DATA_DIR"
        echo "Database:             $DATABASE"
        echo "Server Identity:      $SERVER_IDENTITY"
    fi

    echo

    create_directories
    install_rsqlite

    if [ "$ROLE" = "client" ] || [ "$ROLE" = "both" ]; then
        install_client_config
        create_client_identity
    fi

    if [ "$ROLE" = "server" ] || [ "$ROLE" = "both" ]; then
        create_server_identity
        configure_server_destination
        install_server_config
        install_allowed_identities
    fi

    if [ "$ROLE" = "both" ]; then
        configure_client_server
        add_client_identity_to_acl
    fi

    show_final_report
}


main