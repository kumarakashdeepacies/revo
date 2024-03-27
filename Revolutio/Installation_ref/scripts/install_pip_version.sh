#!/bin/bash

function install_pip_version() {
    pip install --no-cache-dir --upgrade "pip==${REVOLUTIO_PIP_VERSION}" && mkdir -p /root/.local/bin
}

install_pip_version