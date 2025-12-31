# Network Backup Automation

Ansible playbooks for automating backup of network devices (Cisco routers and Check Point firewalls).

## Security

This project uses **Ansible Vault** to encrypt sensitive credentials. Passwords are stored in encrypted format in `group_vars/all/vault.yml`.

## Prerequisites

- Python 3.x
- uv (Python package manager)
- Ansible with network collections

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set up vault password (first time only):
```bash
# Store your vault password securely
echo "your-vault-password" > .vault_pass
chmod 600 .vault_pass
```

## Running Playbooks

### Cisco Router Backup

```bash
# With vault password file
uv run ansible-playbook -i inventory.yml cisco_backup.yml --vault-password-file .vault_pass

# Or prompt for vault password
uv run ansible-playbook -i inventory.yml cisco_backup.yml --ask-vault-pass
```

### Check Point Firewall Backup

```bash
uv run ansible-playbook -i inventory.yml checkpoint_backup.yml --vault-password-file .vault_pass
```

## Managing Vault Secrets

### View encrypted vault:
```bash
uv run ansible-vault view group_vars/all/vault.yml --vault-password-file .vault_pass
```

### Edit vault:
```bash
uv run ansible-vault edit group_vars/all/vault.yml --vault-password-file .vault_pass
```

### Change vault password:
```bash
uv run ansible-vault rekey group_vars/all/vault.yml --vault-password-file .vault_pass
```

## Directory Structure

```
.
├── inventory.yml              # Inventory with vault variable references
├── group_vars/
│   └── all/
│       └── vault.yml          # Encrypted credentials (committed to git)
├── cisco_backup.yml           # Cisco router backup playbook
├── cisco_command.txt          # Commands to execute on Cisco devices
├── checkpoint_backup.yml      # Check Point firewall backup playbook
├── backups/
│   ├── cisco/                 # Cisco router backup outputs
│   └── checkpoint/            # Check Point firewall backups
└── .vault_pass                # Vault password (NOT committed to git)
```

## Vault Variables

The following variables are defined in the encrypted vault:

- `vault_admin_password` - Device login password
- `vault_enable_password_checkpoint` - Check Point enable password
- `vault_enable_password_routers` - Cisco router enable password

## Important Notes

⚠️ **Never commit these files:**
- `.vault_pass` - Your vault password file
- `backups/` - Backup files may contain sensitive data

✅ **Safe to commit:**
- `group_vars/all/vault.yml` - This is encrypted
- `inventory.yml` - References vault variables, no plain text passwords
