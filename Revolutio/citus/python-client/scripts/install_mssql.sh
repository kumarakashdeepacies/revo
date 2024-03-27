#!/bin/bash
set -exuo pipefail
function install_mssql_client() {
    echo
    echo Installing mssql client
    echo
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
    apt-get update -yqq
    apt-get upgrade -yqq
    ACCEPT_EULA=Y apt-get -yqq install -y --no-install-recommends msodbcsql18 mssql-tools18
    rm -rf /var/lib/apt/lists/*
    apt-get autoremove -yqq --purge
    apt-get clean && rm -rf /var/lib/apt/lists/*
}

# Install MsSQL client from Microsoft repositories
if [[ ${INSTALL_MSSQL_CLIENT:="true"} == "true" ]]; then
    install_mssql_client "${@}"
fi