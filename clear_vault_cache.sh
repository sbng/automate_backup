#!/bin/bash
# Clear the cached vault password

cd "$(dirname "$0")"

# Use parent PID - stays constant across multiple script runs
export VAULT_SHELL_PID=$PPID

./vault_password.py --clear
