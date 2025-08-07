#!/usr/bin/env python3
"""
Security verification script for autonote
Checks if the application is properly configured with secure settings
"""

import os
import secrets
from config import Config

def check_secret_key():
    """Check if secret key is properly configured"""
    print("🔐 Checking SECRET_KEY configuration...")
    
    secret_key = Config.SECRET_KEY
    
    if not secret_key:
        print("❌ No SECRET_KEY found!")
        return False
    
    if len(secret_key) < 16:
        print(f"⚠️  SECRET_KEY is too short ({len(secret_key)} chars). Recommended: 32+ chars")
        return False
    
    # Check if it's a default/example value
    unsafe_keys = [
        'your-secret-key-here',
        'supersecretkey',
        'change-me',
        'fallback-secret-key'
    ]
    
    if any(unsafe in secret_key.lower() for unsafe in unsafe_keys):
        print("⚠️  SECRET_KEY appears to be a default/example value!")
        return False
    
    print(f"✅ SECRET_KEY is properly configured ({len(secret_key)} characters)")
    return True

def check_environment():
    """Check environment configuration"""
    print("\n🌍 Checking environment configuration...")
    
    flask_env = os.getenv('FLASK_ENV', 'production')
    print(f"📊 FLASK_ENV: {flask_env}")
    
    if flask_env == 'development':
        print("🔧 Development mode - Debug features enabled")
    elif flask_env == 'production':
        print("🚀 Production mode - Optimized for deployment")
    
    return True

def check_security_headers():
    """Check security-related configuration"""
    print("\n🛡️  Checking security configuration...")
    
    print(f"🍪 Session cookie secure: {Config.SESSION_COOKIE_SECURE}")
    print(f"🔒 Session cookie HTTP only: {Config.SESSION_COOKIE_HTTPONLY}")
    print(f"🌐 Session cookie same site: {Config.SESSION_COOKIE_SAMESITE}")
    
    return True

def check_ai_configuration():
    """Check AI-related configuration"""
    print("\n🤖 Checking AI configuration...")
    
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        if openai_key.startswith('sk-'):
            print("✅ OpenAI API key is configured (fallback available)")
        else:
            print("⚠️  OpenAI API key format looks incorrect")
    else:
        print("📝 No OpenAI API key - using offline AI models only")
    
    return True

def generate_new_key():
    """Generate a new secure key"""
    print("\n🔄 Generating new secure key...")
    new_key = secrets.token_urlsafe(32)
    print(f"🔑 New SECRET_KEY: {new_key}")
    print("\n📝 To use this key:")
    print("1. Update your .env file")
    print("2. Or set SECRET_KEY environment variable")
    print("3. Restart your application")

def main():
    """Main security check function"""
    print("🔍 autonote Security Check")
    print("=" * 50)
    
    checks = [
        check_secret_key(),
        check_environment(),
        check_security_headers(),
        check_ai_configuration()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("✅ All security checks passed!")
        print("🚀 Your autonote application is securely configured.")
    else:
        print("⚠️  Some security issues found.")
        print("🔧 Consider running: python generate_env.py")
    
    # Offer to generate new key
    response = input("\n🔄 Generate a new secure key? (y/N): ").lower()
    if response == 'y':
        generate_new_key()

if __name__ == "__main__":
    main()
