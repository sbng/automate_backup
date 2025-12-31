#!/usr/bin/expect -f
set timeout 60
set host [lindex $argv 0]
set password [lindex $argv 1]
set expert_password [lindex $argv 2]
set backup_file [lindex $argv 3]
set dest_file [lindex $argv 4]

spawn scp -o StrictHostKeyChecking=no -o KexAlgorithms=+diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-rsa admin@$host:/var/CPbackup/backups/$backup_file $dest_file
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Enter expert password:" {
        send "$expert_password\r"
        exp_continue
    }
    eof
}
