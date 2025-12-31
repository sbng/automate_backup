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

### Quick Method (Password Caching - 30 min timeout)

The easiest way to run backups with automatic password caching:

```bash
# Run Cisco backup - prompts for password first time only
./run_cisco_backup.sh

# Run Checkpoint backup - uses cached password if within 30 minutes
./run_checkpoint_backup.sh

# Clear cached password manually (auto-expires after 30 minutes)
./clear_vault_cache.sh
```

**How it works:**
- First run prompts for vault password
- Password cached in `~/.ansible_vault_cache_sessions/vault_cache_<PID>.pkl` for 30 minutes
- Cache is **session-specific** - only accessible to current shell and its child processes
- Subsequent runs within 30 minutes use cached password (no prompt)
- Cache automatically expires after 30 minutes
- Cache automatically deleted when shell session exits
- Cache file has restricted permissions (0600) for security
- Directory has restricted permissions (0700) - owner only access

### Manual Method (Prompt Every Time)

```bash
# With vault password file
uv run ansible-playbook -i inventory.yml cisco_backup.yml --vault-password-file .vault_pass

# Or prompt for vault password each time
uv run ansible-playbook -i inventory.yml cisco_backup.yml --ask-vault-pass
```

### Cisco Router Backup

```bash
# Using cache (recommended)
./run_cisco_backup.sh

# Manual with vault password file
uv run ansible-playbook -i inventory.yml cisco_backup.yml --vault-password-file .vault_pass

# Or prompt for vault password
uv run ansible-playbook -i inventory.yml cisco_backup.yml --ask-vault-pass
```

### Check Point Firewall Backup

```bash
# Using cache (recommended)
./run_checkpoint_backup.sh

# Manual
uv run ansible-playbook -i inventory.yml checkpoint_backup.yml --vault-password-file .vault_pass
```

## Password Cache Management

### Configure Cache Timeout

Edit `vault_password.py` to change how long the password is cached:

```python
# In vault_password.py, line 18:
CACHE_TIMEOUT_MINUTES = 30  # Change this value

# Examples:
CACHE_TIMEOUT_MINUTES = 15   # Cache for 15 minutes
CACHE_TIMEOUT_MINUTES = 60   # Cache for 1 hour
CACHE_TIMEOUT_MINUTES = 120  # Cache for 2 hours
CACHE_TIMEOUT_MINUTES = 5    # Cache for 5 minutes (more secure)
```

### Cache Commands

```bash
# Clear cached password for current session
./clear_vault_cache.sh

# Check cache status for current session
ls -la ~/.ansible_vault_cache_sessions/

# When running, you'll see cache status:
# "Password cached for 30 minutes (session 12345)" - when password is first entered
# "Using cached password (expires in 25 minutes, session 12345)" - when using cache
```

### Security Features

🔒 **Session Isolation**
- Each shell session has its own password cache
- Cache cannot be accessed by other shell sessions
- Cache is automatically deleted when shell exits

🔒 **File Permissions**
- Cache files: 0600 (owner read/write only)
- Cache directory: 0700 (owner access only)
- Permissions are verified before reading cache

🔒 **Process Validation**
- Verifies parent shell process is still running
- Rejects cache if shell session has ended
- Auto-cleanup of orphaned cache files

🔒 **Time-based Expiration**
- Password expires after configured timeout
- Default: 30 minutes (configurable)
- Old caches automatically cleaned up

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
├── inventory.yml                   # Inventory with vault variable references
├── group_vars/
│   └── all/
│       └── vault.yml               # Encrypted credentials (committed to git)
├── cisco_backup.yml                # Cisco router backup playbook
├── cisco_command.txt               # Commands to execute on Cisco devices
├── checkpoint_backup.yml           # Check Point firewall backup playbook
├── vault_password.py               # Vault password caching script (30 min timeout)
├── run_cisco_backup.sh             # Wrapper script for Cisco backup
├── run_checkpoint_backup.sh        # Wrapper script for Checkpoint backup
├── clear_vault_cache.sh            # Clear password cache
├── backups/
│   ├── cisco/                      # Cisco router backup outputs
│   └── checkpoint/                 # Check Point firewall backups
├── .vault_pass                     # Optional: Vault password file (NOT committed)
└── ~/.ansible_vault_cache_sessions/ # Session-specific password caches (NOT committed)
    └── vault_cache_<PID>.pkl       # Cache for shell PID (auto-deleted on exit)
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
