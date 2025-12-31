# Vault Password Caching System

## Overview

The `vault_password.py` script provides secure, session-based password caching for Ansible Vault. It allows you to enter your vault password once per shell session and automatically reuses it for 30 minutes, eliminating the need to type your password repeatedly while maintaining strong security.

## How It Works

### Simple Explanation

Think of it like a secure notebook that:
- 🔒 Each terminal window has its own separate page
- ⏱️ Pages automatically shred themselves after 30 minutes
- 🚪 Pages are destroyed when you close the terminal
- 👁️ Only you can read your own pages
- 🧹 Old pages from closed terminals are automatically cleaned up **every time you run a backup**

### Technical Flow

```
First Run in Terminal 1:
  You run: ./run_cisco_backup.sh
    ↓
  Script cleans up expired cache files from previous sessions
    ↓
  "Cleaned up 3 expired cache file(s)" (if any old caches found)
    ↓
  Script asks: "Vault password: ?"
    ↓
  You enter password
    ↓
  Password saved to: ~/.ansible_vault_cache_sessions/vault_cache_12345.pkl
    ↓
  "Password cached for 30 minutes (session 12345)"
    ↓
  Backup runs successfully

Second Run in Same Terminal (within 30 min):
  You run: ./run_cisco_backup.sh
    ↓
  Script checks for expired caches (finds none)
    ↓
  Script checks cache file for session 12345
    ↓
  Found valid password!
    ↓
  "Using cached password (expires in 25 minutes, session 12345)"
    ↓
  Backup runs without prompting

After 30 Minutes:
  You run: ./run_cisco_backup.sh
    ↓
  Script checks for expired caches
    ↓
  Finds vault_cache_12345.pkl is expired
    ↓
  "Cleaned up 1 expired cache file(s)"
    ↓
  No valid cache for this session
    ↓
  Script asks: "Vault password: ?"
    ↓
  New cache created

New Terminal Window:
  You run: ./run_cisco_backup.sh
    ↓
  Script checks cache file for this terminal's PID
    ↓
  No cache for this session
    ↓
  "Note: Password cached in 1 other shell session(s): [12345]"
  "Creating separate cache for this session (PID: 67890)"
    ↓
  Script asks: "Vault password: ?"
    ↓
  New cache created for this terminal
```

## Security Features

### 🔐 Session Isolation

**What it means**: Each terminal window has its own password cache.

**Why it matters**: 
- If someone gains access to one terminal, they can't steal passwords from your other terminals
- Closing a terminal automatically invalidates its cached password
- No password sharing between different terminals

**Example**:
```bash
Terminal 1: Password cached as vault_cache_12345.pkl
Terminal 2: Password cached as vault_cache_67890.pkl
Terminal 3: Password cached as vault_cache_11111.pkl

Each is completely isolated from the others.
```

### ⏱️ Automatic Expiration

**What it means**: Cached passwords automatically expire after the configured time (default: 30 minutes).

**Why it matters**:
- Limits the window of opportunity if someone gains access to your computer
- Forces re-authentication after a reasonable time
- You can configure the timeout to match your security requirements

**Timeline**:
```
3:00 PM - Password cached
3:15 PM - Still valid (15 minutes left)
3:29 PM - Still valid (1 minute left)
3:30 PM - EXPIRED - prompts for password again
```

### 🚪 Process Validation

**What it means**: The script verifies your shell is still running before using the cached password.

**Why it matters**:
- If your terminal crashes or is force-closed, the cache becomes invalid
- Prevents stale passwords from being used
- Ensures cache is tied to an active session

**How it works**:
```python
1. Cache stores shell PID (Process ID): 12345
2. Before using cache, checks: "Is process 12345 still running?"
3. If NO → Delete cache, prompt for password
4. If YES → Use cached password
```

### 🔒 File Permissions

**What it means**: Cache files and directories have strict permissions that only you can access.

**Why it matters**:
- Other users on the system cannot read your cached passwords
- Prevents privilege escalation attacks
- Meets security compliance requirements

**Permission Details**:
```
Directory: ~/.ansible_vault_cache_sessions/
  Permissions: 0700 (drwx------) 
  Meaning: Only owner can read, write, execute

Files: vault_cache_12345.pkl
  Permissions: 0600 (-rw-------)
  Meaning: Only owner can read and write
```

### 🛡️ Permission Verification

**What it means**: The script double-checks permissions before trusting a cache file.

**Why it matters**:
- Detects if permissions were accidentally changed
- Refuses to use cache with insecure permissions
- Automatically deletes compromised cache files

**Example**:
```bash
# If someone tries to change permissions:
chmod 644 ~/.ansible_vault_cache_sessions/vault_cache_12345.pkl

# Next run will see:
"Warning: Cache file has insecure permissions, ignoring"
# Cache deleted and fresh password prompt shown
```

### 🧹 Automatic Cleanup

**What it means**: Old cache files from closed terminals and expired caches are automatically removed every time you run a backup script.

**Why it matters**:
- Prevents disk space waste from accumulating cache files
- Reduces attack surface (fewer old password files lying around)
- Keeps the system tidy without manual intervention
- Enhances security by promptly removing expired passwords

**When cleanup happens**:
```bash
# Cleanup runs automatically:
1. Every time you run: ./run_cisco_backup.sh
2. Every time you run: ./run_checkpoint_backup.sh
3. When you manually run: ./clear_vault_cache.sh

# Removes cache files when:
- Parent shell process no longer exists (terminal closed)
- Cache has expired (>30 minutes old)
- Skips your current session's cache (keeps it safe)
```

**Example output**:
```bash
$ ./run_cisco_backup.sh
Cleaned up 3 expired cache file(s)
Using cached password (expires in 20 minutes, session 12345)
```

## Configuration

### Changing Cache Timeout

Edit `vault_password.py` (line 22):

```python
# Default: 30 minutes
CACHE_TIMEOUT_MINUTES = 30

# Examples:
CACHE_TIMEOUT_MINUTES = 15   # More secure: 15 minutes
CACHE_TIMEOUT_MINUTES = 60   # More convenient: 1 hour
CACHE_TIMEOUT_MINUTES = 5    # Very secure: 5 minutes
CACHE_TIMEOUT_MINUTES = 120  # Relaxed: 2 hours
```

After changing, the new timeout applies to newly cached passwords.

## Usage Examples

### Scenario 1: Normal Workflow (Single Terminal)

```bash
# 9:00 AM - First backup (may clean up old caches)
$ ./run_cisco_backup.sh
Cleaned up 2 expired cache file(s)
Vault password: ********
Password cached for 30 minutes (session 12345)
[Backup runs...]

# 9:10 AM - Second backup (same terminal)
$ ./run_cisco_backup.sh
Using cached password (expires in 20 minutes, session 12345)
[Backup runs immediately, no password prompt]

# 9:25 AM - Third backup (same terminal)
$ ./run_cisco_backup.sh
Using cached password (expires in 5 minutes, session 12345)
[Backup runs immediately]

# 9:35 AM - Fourth backup (cache expired)
$ ./run_cisco_backup.sh
Cleaned up 1 expired cache file(s)
Vault password: ********
Password cached for 30 minutes (session 12345)
[Backup runs...]
```

### Scenario 2: Multiple Terminals

```bash
# Terminal 1
$ ./run_cisco_backup.sh
Vault password: ********
Password cached for 30 minutes (session 12345)

# Open Terminal 2 (new window)
$ ./run_cisco_backup.sh
Note: Password cached in 1 other shell session(s): [12345]
Creating separate cache for this session (PID: 67890)
No cached password for current shell session (PID: 67890)
Vault password: ********
Password cached for 30 minutes (session 67890)

# Back to Terminal 1
$ ./run_cisco_backup.sh
Using cached password (expires in 25 minutes, session 12345)
# (Still uses its own cache)

# Back to Terminal 2
$ ./run_cisco_backup.sh
Using cached password (expires in 28 minutes, session 67890)
# (Uses its own cache)
```

### Scenario 3: Clearing Cache Manually

```bash
# After entering password
$ ./run_cisco_backup.sh
Vault password: ********
Password cached for 30 minutes (session 12345)

# Need to leave computer, want to clear password
$ ./clear_vault_cache.sh
Vault password cache cleared for session 12345.

# Next run prompts again
$ ./run_cisco_backup.sh
Vault password: ********
```

### Scenario 4: Terminal Crashes

```bash
# Terminal 1 - Cache password
$ ./run_cisco_backup.sh
Vault password: ********
Password cached for 30 minutes (session 12345)

# Terminal crashes or is force-closed
# File vault_cache_12345.pkl still exists on disk

# Open new Terminal 2
$ ./run_cisco_backup.sh
# Script checks if process 12345 is running → NO
# Deletes orphaned cache file
# Prompts for password
Vault password: ********
```

## Command Reference

### Run Backups (with caching)

```bash
# Cisco routers backup
./run_cisco_backup.sh

# Checkpoint firewall backup
./run_checkpoint_backup.sh
```

### Clear Cached Password

```bash
# Clear cache for current session
./clear_vault_cache.sh

# Output:
# Vault password cache cleared for session 12345.
# Cleaned up 2 old cache file(s)  # (if any orphaned caches found)
```

### Check Cache Status

```bash
# List all cached sessions
ls -la ~/.ansible_vault_cache_sessions/

# Example output:
# drwx------ 2 user user 4096 Dec 31 09:00 .
# -rw------- 1 user user  245 Dec 31 09:00 vault_cache_12345.pkl
# -rw------- 1 user user  245 Dec 31 09:05 vault_cache_67890.pkl
```

### Check Your Shell PID

```bash
# To see your current shell's PID
echo $$

# The cache file for this session will be:
# ~/.ansible_vault_cache_sessions/vault_cache_<PID>.pkl
```

## Troubleshooting

### Problem: Always Prompting for Password

**Possible Causes**:
1. Cache timeout set too short
2. Opening new terminals (each needs its own password entry - by design)
3. Cache file deleted or corrupted
4. Permission issues
5. Using wrong shell PID

**Solutions**:
```bash
# Check if cache directory exists
ls -la ~/.ansible_vault_cache_sessions/

# Check permissions
ls -la ~/.ansible_vault_cache_sessions/vault_cache_*.pkl
# Should show: -rw------- (0600)

# Check your shell PID
echo $PPID
# Look for vault_cache_<PPID>.pkl

# Increase timeout in vault_password.py:
CACHE_TIMEOUT_MINUTES = 60  # Change from 30 to 60

# Enable debug to see what's happening
VAULT_SHELL_PID=$PPID python3 vault_password.py
```

### Problem: "Warning: Cache file has insecure permissions"

**Cause**: File permissions were changed (not 0600)

**Solution**:
```bash
# The script automatically deletes the insecure cache
# Just enter password again, new cache will be created with correct permissions
```

### Problem: Cache Not Shared Between Terminals

**This is not a problem** - it's a security feature!

**Explanation**: 
Each terminal has its own cache for security. This is intentional.

**If you really want to share** (not recommended):
Edit `vault_password.py` line 27 and use a static filename instead of PID-based, but this reduces security significantly.

### Problem: Old Cache Files Accumulating

**This should not happen anymore** - automatic cleanup is enabled!

**If it does happen**:
```bash
# Check for orphaned caches
ls -la ~/.ansible_vault_cache_sessions/

# Automatic cleanup should handle this, but manual cleanup:
./clear_vault_cache.sh

# Or delete all caches
rm -rf ~/.ansible_vault_cache_sessions/

# Next run will recreate the directory and cache
```

**Note**: As of the latest update, cleanup happens automatically every time you run a backup, so old files should not accumulate.

## Security Best Practices

### ✅ DO:
- Use the default 30-minute timeout (good balance)
- Clear cache before leaving your computer: `./clear_vault_cache.sh`
- Keep cache files in your home directory (default location)
- Review cache directory permissions occasionally
- Use different passwords in different environments (dev/prod)

### ❌ DON'T:
- Don't set timeout too long (>2 hours increases risk)
- Don't share cache files between users
- Don't change cache file permissions
- Don't commit cache files to git (already in .gitignore)
- Don't store vault password in plain text files

## File Locations

```
Project Files:
  ./vault_password.py              # Main caching script
  ./run_cisco_backup.sh            # Wrapper for Cisco backup
  ./run_checkpoint_backup.sh       # Wrapper for Checkpoint backup
  ./clear_vault_cache.sh           # Clear cache script

Cache Storage:
  ~/.ansible_vault_cache_sessions/          # Cache directory
  ~/.ansible_vault_cache_sessions/vault_cache_12345.pkl  # Session cache

Not Used Anymore:
  ~/.ansible_vault_cache           # Old single-file cache (deprecated)
```

## Technical Details

### Cache File Format

The cache file is a Python pickle containing:

```python
{
    'timestamp': 1735614000.0,      # Unix timestamp when cached
    'password': 'your_vault_pass',   # The actual password
    'shell_pid': 12345               # Parent shell process ID (from $PPID)
}
```

### Shell PID Detection

Uses `$PPID` (parent process ID) exported by wrapper scripts:
- Wrapper scripts set: `export VAULT_SHELL_PID=$PPID`
- `$PPID` is the parent shell PID (stays constant across script runs)
- **Not** `$$` (current script PID, which changes every run)
- Ensures same cache file is reused within the same terminal session

### Process Detection

Uses `os.kill(pid, 0)` to check if process exists:
- Signal 0 doesn't kill the process
- Returns True if process is running
- Returns False if process doesn't exist
- Works across all Unix-like systems

### Permission Checking

Uses bitwise operations to verify permissions:

```python
stat_info.st_mode & 0o077
# Checks if group (0o070) or other (0o007) have ANY permissions
# Result of 0 means only owner has permissions (secure)
# Non-zero means insecure permissions
```

### Automatic Cleanup Algorithm

```python
# Runs at start of get_vault_password()
For each cache file in directory:
  1. Extract PID from filename (vault_cache_12345.pkl → 12345)
  2. Skip if PID matches current session (keep our own cache)
  3. Check if PID process is running
     - If NO → Delete cache file (shell closed)
  4. Check file modification time
     - If age > TIMEOUT_SECONDS → Delete cache file (expired)
  5. Count deletions and report to user
```

## Version History

- **v4.0** (Current) - Automatic cleanup on every run, using $PPID for stable shell tracking
- **v3.0** - Session-based caching with multi-terminal support
- **v2.0** - Added manual cleanup and process validation
- **v1.0** - Initial single-file cache implementation

## Support

For issues or questions:
1. Check this documentation
2. Review the troubleshooting section
3. Check script comments in `vault_password.py`
4. Review `README_VAULT.md` for Ansible Vault basics

## License

This script is part of the automate_backup project and follows the same license.
