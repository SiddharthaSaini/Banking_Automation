#!/usr/bin/env python3
"""
Generate a secure secret key for Flask application
Run this script to generate a random secret key for your deployment
"""

import secrets

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_hex(32)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("Generated SECRET_KEY for your Flask application:")
    print(f"SECRET_KEY={secret_key}")
    print("\nCopy this value and set it as an environment variable in Render.")
