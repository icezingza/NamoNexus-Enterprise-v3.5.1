#!/usr/bin/env python3
"""
Generate secure secrets for NamoNexus Enterprise v3.5.1
"""

import secrets
import os
import sys

def generate_token(length: int = 32) -> str:
    """Generate a secure URL-safe token"""
    return secrets.token_urlsafe(length)

def generate_cipher_key(length: int = 32) -> str:
    """Generate a secure cipher key for SQLCipher"""
    return secrets.token_urlsafe(length)

def main():
    print("=" * 60)
    print("NamoNexus Enterprise v3.5.1 - Secret Key Generator")
    print("=" * 60)
    print()
    
    # Generate tokens
    namo_nexus_token = generate_token(32)
    db_cipher_key = generate_cipher_key(32)
    
    print("✅ Generated secure keys:")
    print()
    print(f"NAMO_NEXUS_TOKEN={namo_nexus_token}")
    print(f"DB_CIPHER_KEY={db_cipher_key}")
    print()
    print("=" * 60)
    print("⚠️  IMPORTANT SECURITY NOTICE ⚠️")
    print("=" * 60)
    print("1. COPY these values to your .env file")
    print("2. DO NOT commit these keys to Git")
    print("3. Use DIFFERENT keys for each environment (dev/staging/prod)")
    print("4. Store in Password Manager (Bitwarden, 1Password, etc.)")
    print("=" * 60)
    
    # Ask to save to .env
    print()
    response = input("Save to .env file? (y/n): ")
    if response.lower() == 'y':
        try:
            with open('.env', 'a') as f:
                f.write(f"\n# Generated on {os.popen('date').read().strip()}\n")
                f.write(f"NAMO_NEXUS_TOKEN={namo_nexus_token}\n")
                f.write(f"DB_CIPHER_KEY={db_cipher_key}\n")
            print("✅ Saved to .env file")
        except Exception as e:
            print(f"❌ Error saving to .env: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
