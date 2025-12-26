#!/usr/bin/env python3
import sys
import paramiko
import base64
import time
import re

def fetch_backup(host, username, password, expert_password, backup_file, output_file):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect
    print(f"Connecting to {host}...")
    client.connect(host, username=username, password=password, 
                   look_for_keys=False, allow_agent=False)
    
    # Start shell with larger window size for better performance
    shell = client.invoke_shell(width=200, height=50)
    shell.settimeout(300)  # 5 minute timeout for large files
    time.sleep(2)
    initial_output = shell.recv(16384).decode()
    print(f"Initial connection established")
    
    # Enter expert mode
    print("Entering expert mode...")
    shell.send('expert\n')
    time.sleep(1)
    
    # Wait for password prompt
    output = ''
    for _ in range(5):
        if shell.recv_ready():
            output += shell.recv(8192).decode()
        if 'Enter expert password:' in output:
            break
        time.sleep(0.5)
    
    # Send expert password
    print("Sending expert password...")
    shell.send(f'{expert_password}\n')
    time.sleep(2)
    
    # Clear the buffer
    if shell.recv_ready():
        shell.recv(16384).decode()
    
    # Run base64 command
    print(f"Encoding {backup_file} (this may take a while for large files)...")
    shell.send(f'base64 /var/log/CPbackup/backups/{backup_file}\n')
    time.sleep(2)
    
    # Collect all output - need to wait for large files (up to several GB)
    print("Collecting base64 output (please wait, this can take several minutes for large backups)...")
    all_output = ''
    no_data_count = 0
    max_wait_cycles = 60  # Wait up to 30 seconds without data before giving up
    chunk_count = 0
    
    while no_data_count < max_wait_cycles:
        if shell.recv_ready():
            # Use larger buffer for better performance with GB-sized files
            chunk = shell.recv(131072).decode('ascii', errors='ignore')  # 128KB chunks, ignore non-ASCII
            all_output += chunk
            chunk_count += 1
            if chunk_count % 100 == 0:
                print(f"  Received {len(all_output) / 1024 / 1024:.1f} MB so far...")
            no_data_count = 0
        else:
            no_data_count += 1
            time.sleep(0.5)
    
    # Send exit to close expert mode
    shell.send('exit\n')
    time.sleep(0.5)
    
    # Close connection
    shell.close()
    client.close()
    
    print(f"Received {len(all_output) / 1024 / 1024:.1f} MB of output")
    
    # Extract base64 data (lines that look like base64)
    print("Extracting and decoding base64 data...")
    lines = all_output.split('\n')
    base64_lines = []
    for line in lines:
        line = line.strip().replace('\r', '')
        # Match lines with at least 40 chars of valid base64
        if len(line) >= 40 and re.match(r'^[A-Za-z0-9+/=]+$', line):
            base64_lines.append(line)
    
    print(f"Found {len(base64_lines)} base64 lines")
    
    # Decode and save
    if base64_lines:
        base64_data = ''.join(base64_lines)
        print(f"Total base64 data: {len(base64_data) / 1024 / 1024:.1f} MB")
        try:
            print("Decoding base64...")
            binary_data = base64.b64decode(base64_data)
            print(f"Writing {len(binary_data) / 1024 / 1024:.1f} MB to {output_file}...")
            with open(output_file, 'wb') as f:
                f.write(binary_data)
            print(f"✓ Successfully downloaded {len(binary_data) / 1024 / 1024:.1f} MB to {output_file}")
            return True
        except Exception as e:
            print(f"Failed to decode base64: {e}")
            print(f"First base64 line: {base64_lines[0][:100] if base64_lines else 'none'}")
            print(f"Last base64 line: {base64_lines[-1][:100] if base64_lines else 'none'}")
    else:
        print("No base64 data found in output")
        print("Output sample (first 2000 chars):")
        print(all_output[:2000])
    
    return False

if __name__ == '__main__':
    if len(sys.argv) != 7:
        print("Usage: fetch_backup.py <host> <username> <password> <expert_password> <backup_file> <output_file>")
        sys.exit(1)
    
    success = fetch_backup(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
    sys.exit(0 if success else 1)
