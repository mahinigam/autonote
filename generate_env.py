#!/usr/bin/env python3
"""
Utility script to generate secure environment variables
Run this script to generate secure keys for your .env file
"""

import secrets
import os

def generate_secret_key(length=32):
    """Generate a cryptographically secure secret key"""
    return secrets.token_urlsafe(length)

def generate_env_file():
    """Generate a .env file with secure values"""
    
    print("Generating secure environment variables...")
    
    # Generate secure secret key
    secret_key = generate_secret_key(32)
    
    # Check if .env already exists
    env_path = '.env'
    if os.path.exists(env_path):
        response = input("WARNING: .env file already exists. Overwrite? (y/N): ").lower()
        if response != 'y':
            print("Cancelled. Your existing .env file is unchanged.")
            return
    
    # Create .env content
    env_content = f"""# Environment variables for local development
# Generated on {os.popen('date').read().strip()}

# Flask Configuration
SECRET_KEY={secret_key}
FLASK_ENV=development

# Optional: Enable debug mode for development
# FLASK_DEBUG=True
"""
    
    # Write to .env file
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("Successfully generated .env file!")
        print(f"Generated SECRET_KEY: {secret_key}")
        print("\nNext steps:")
        print("1. Review the .env file")
        print("2. Never commit the .env file to version control")
        
    except Exception as e:
        print(f"Error creating .env file: {e}")

def generate_production_key():
    """Generate a production-ready secret key"""
    key = generate_secret_key(64)  # Longer key for production
    print("Production Secret Key (64 characters):")
    print(f"SECRET_KEY={key}")
    print("\nIMPORTANT:")
    print("- Use this key in your production environment variables")
    print("- Never expose this key in logs or version control")
    print("- Store it securely in your deployment platform")

if __name__ == "__main__":
    print("AutoNote Environment Setup")
    print("=" * 40)
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Generate .env file for local development")
        print("2. Generate production secret key only")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            generate_env_file()
        elif choice == '2':
            generate_production_key()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
