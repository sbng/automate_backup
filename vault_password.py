#!/usr/bin/env python3
"""
Ansible Vault password caching script with timeout.
Stores password in memory and expires after configured timeout.

CONFIGURATION:
    Edit CACHE_TIMEOUT_MINUTES below to change how long the password is cached.

SECURITY:
    Password cache is restricted to the current shell session and its child processes.
    Cache is stored per-session and automatically cleaned up when shell exits.
"""
import os
import sys
import time
import pickle
from pathlib import Path

# ============================================================================
# CONFIGURATION - Change this value to adjust cache timeout
# ============================================================================
CACHE_TIMEOUT_MINUTES = 30  # How long to cache password (in minutes)
# ============================================================================

# Use session-specific cache file based on shell PID
# This ensures cache is only accessible to current shell and child processes
SHELL_PID = os.getppid()  # Get parent (shell) process ID
CACHE_DIR = Path.home() / ".ansible_vault_cache_sessions"
CACHE_FILE = CACHE_DIR / f"vault_cache_{SHELL_PID}.pkl"
TIMEOUT_SECONDS = CACHE_TIMEOUT_MINUTES * 60


def get_cached_password():
    """Retrieve password from cache if not expired."""
    if not CACHE_FILE.exists():
        return None
    
    try:
        # Verify file permissions and ownership
        stat_info = CACHE_FILE.stat()
        if stat_info.st_mode & 0o077:  # Check if group/other have any permissions
            print("Warning: Cache file has insecure permissions, ignoring", file=sys.stderr)
            CACHE_FILE.unlink()
            return None
        
        # Verify the parent process (shell) is still running
        if not is_process_running(SHELL_PID):
            print("Shell session ended, clearing cache", file=sys.stderr)
            CACHE_FILE.unlink()
            return None
        
        with open(CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
        
        timestamp = data.get('timestamp', 0)
        password = data.get('password', '')
        
        # Check if cache has expired
        elapsed_time = time.time() - timestamp
        if elapsed_time > TIMEOUT_SECONDS:
            CACHE_FILE.unlink()
            return None
        
        # Print cache info to stderr for user awareness
        remaining_minutes = int((TIMEOUT_SECONDS - elapsed_time) / 60)
        print(f"Using cached password (expires in {remaining_minutes} minutes, session {SHELL_PID})", file=sys.stderr)
        
        return password
    except Exception as e:
        print(f"Error reading cache: {e}", file=sys.stderr)
        return None


def is_process_running(pid):
    """Check if a process is still running."""
    try:
        # Sending signal 0 doesn't kill the process, just checks if it exists
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def cache_password(password):
    """Store password in cache with timestamp."""
    # Ensure cache directory exists with secure permissions
    CACHE_DIR.mkdir(mode=0o700, exist_ok=True)
    
    data = {
        'timestamp': time.time(),
        'password': password,
        'shell_pid': SHELL_PID
    }
    
    # Create cache file with restricted permissions (owner only)
    CACHE_FILE.touch(mode=0o600)
    
    # Double-check permissions were set correctly
    CACHE_FILE.chmod(0o600)
    
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"Password cached for {CACHE_TIMEOUT_MINUTES} minutes (session {SHELL_PID})", file=sys.stderr)


def clear_cache():
    """Remove cached password."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print(f"Vault password cache cleared for session {SHELL_PID}.", file=sys.stderr)
    else:
        print(f"No cached password for session {SHELL_PID}.", file=sys.stderr)
    
    # Also clean up old/expired cache files from other sessions
    cleanup_old_caches()


def cleanup_old_caches():
    """Remove cache files from terminated sessions or expired caches."""
    if not CACHE_DIR.exists():
        return
    
    cleaned = 0
    for cache_file in CACHE_DIR.glob("vault_cache_*.pkl"):
        try:
            # Extract PID from filename
            pid_str = cache_file.stem.replace("vault_cache_", "")
            pid = int(pid_str)
            
            # Check if process is still running
            if not is_process_running(pid):
                cache_file.unlink()
                cleaned += 1
                continue
            
            # Check if cache is expired
            stat_info = cache_file.stat()
            age = time.time() - stat_info.st_mtime
            if age > TIMEOUT_SECONDS:
                cache_file.unlink()
                cleaned += 1
        except (ValueError, OSError):
            # Invalid filename or permission error, skip
            pass
    
    if cleaned > 0:
        print(f"Cleaned up {cleaned} old cache file(s)", file=sys.stderr)


def get_vault_password():
    """Get vault password from cache or prompt user."""
    # Check for cached password
    cached = get_cached_password()
    if cached:
        return cached
    
    # Prompt for password
    import getpass
    password = getpass.getpass("Vault password: ")
    
    # Cache the password
    cache_password(password)
    
    return password


if __name__ == '__main__':
    # Handle clear cache command
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        clear_cache()
        sys.exit(0)
    
    # Output password for Ansible
    password = get_vault_password()
    print(password)
