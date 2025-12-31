#!/usr/bin/env python3
"""
Ansible Vault password caching script with timeout.
Stores password in memory and expires after configured timeout.

CONFIGURATION:
    Edit CACHE_TIMEOUT_MINUTES below to change how long the password is cached.
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

CACHE_FILE = Path.home() / ".ansible_vault_cache"
TIMEOUT_SECONDS = CACHE_TIMEOUT_MINUTES * 60


def get_cached_password():
    """Retrieve password from cache if not expired."""
    if not CACHE_FILE.exists():
        return None
    
    try:
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
        print(f"Using cached password (expires in {remaining_minutes} minutes)", file=sys.stderr)
        
        return password
    except Exception:
        return None


def cache_password(password):
    """Store password in cache with timestamp."""
    data = {
        'timestamp': time.time(),
        'password': password
    }
    
    # Create cache file with restricted permissions
    CACHE_FILE.touch(mode=0o600)
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(data, f)
    
    print(f"Password cached for {CACHE_TIMEOUT_MINUTES} minutes", file=sys.stderr)


def clear_cache():
    """Remove cached password."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print("Vault password cache cleared.", file=sys.stderr)


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
