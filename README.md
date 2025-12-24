# Check Point Backup Automation

Automated backup solution for Check Point firewalls using Ansible.

## Features

- ✅ Automated backup creation on Check Point devices
- ✅ Downloads backup archives (.tgz) and metadata files (.info)
- ✅ Handles large backups (GB-sized files)
- ✅ Standalone binary - no Python installation required on control node
- ✅ Base64 transfer method for reliable file transfer through clish/expert mode

## Requirements

- Ansible (installed via uv)
- SSH access to Check Point device
- sshpass installed on control node

## Quick Start

```bash
# Run the backup playbook
uv run ansible-playbook -i inventory.yml checkpoint_backup.yml
```

## Files

- `inventory.yml` - Ansible inventory with Check Point device details
- `checkpoint_backup.yml` - Main playbook for backup and download
- `fetch_backup` - Standalone binary for downloading backups (16MB)
- `fetch_backup.py` - Source code for the download tool
- `backups/` - Directory where backups are stored

## How It Works

1. Connects to Check Point device via SSH (clish mode)
2. Creates a new backup using `add backup local`
3. Lists all available backups
4. Enters expert mode to access the filesystem
5. Base64 encodes the backup file for safe transfer
6. Downloads and decodes both .tgz archive and .info metadata file
7. Saves files to `./backups/` directory

## Rebuilding the Binary

If you make changes to `fetch_backup.py`:

```bash
uv run pyinstaller --onefile --name fetch_backup fetch_backup.py
cp dist/fetch_backup .
```
