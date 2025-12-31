#!/bin/bash
# Clear the cached vault password

cd "$(dirname "$0")"
export VAULT_SHELL_PID=$$
./vault_password.py --clear
