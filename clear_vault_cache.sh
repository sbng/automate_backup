#!/bin/bash
# Clear the cached vault password

cd "$(dirname "$0")"
./vault_password.py --clear
