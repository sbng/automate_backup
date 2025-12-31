#!/bin/bash
# Wrapper script to run Checkpoint backup with cached vault password

cd "$(dirname "$0")"
uv run ansible-playbook -i inventory.yml checkpoint_backup.yml --vault-password-file ./vault_password.py "$@"
