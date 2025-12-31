#!/bin/bash
# Wrapper script to run Cisco backup with cached vault password

cd "$(dirname "$0")"
uv run ansible-playbook -i inventory.yml cisco_backup.yml --vault-password-file ./vault_password.py "$@"
