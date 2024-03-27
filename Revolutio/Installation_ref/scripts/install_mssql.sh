#!/bin/bash
set -exuo pipefail
function install_mssql_client() {
    echo
    echo Installing mssql client
    echo
    apt-get remove -y odbcinst odbcinst1debian2 unixodbc unixodbc-common
    apt-get autoremove -yqq --purge
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg
    curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt-get update -yqq
    # apt-get upgrade -yqq
    apt-get install -y unixodbc-dev unixodbc odbcinst1debian2 odbcinst
    ACCEPT_EULA=Y apt-get -yqq install -y --no-install-recommends msodbcsql18 mssql-tools18
    rm -rf /var/lib/apt/lists/*
    apt-get autoremove -yqq --purge
    apt-get clean && rm -rf /var/lib/apt/lists/*
}

# Install MsSQL client from Microsoft repositories
if [[ ${INSTALL_MSSQL_CLIENT:="true"} == "true" ]]; then
    install_mssql_client "${@}"
fi