#!/bin/bash
# Wrapper script to run Cisco backup with cached vault password

cd "$(dirname "$0")"

# Use parent PID - stays constant across multiple script runs
export VAULT_SHELL_PID=$PPID

uv run ansible-playbook -i inventory.yml cisco_backup.yml --vault-password-file ./vault_password.py "$@"
