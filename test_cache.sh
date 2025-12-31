#!/bin/bash
export VAULT_SHELL_PID=$$
echo "Shell PID for this session: $$"
echo "Run 1:"
echo "mypassword123" | python3 vault_password.py
echo ""
echo "Run 2 (should use cache):"
echo "should_not_be_asked" | python3 vault_password.py
