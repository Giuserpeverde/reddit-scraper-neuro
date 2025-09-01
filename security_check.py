#!/usr/bin/env python3
"""
Security Verification Script for Reddit Scraper Deployment
Checks for common security issues before deploying to Streamlit Cloud
"""

import os
import re
import sys
from pathlib import Path

def check_sensitive_files():
    """Check for sensitive files that shouldn't be in the repository."""
    sensitive_files = [
        '.env',
        '.env.local',
        '.env.production',
        'secrets.json',
        'config.json',
        'credentials.json'
    ]
    
    found_sensitive = []
    for file in sensitive_files:
        if os.path.exists(file):
            found_sensitive.append(file)
    
    if found_sensitive:
        print(f"❌ Found sensitive files: {found_sensitive}")
        return False
    else:
        print("✅ No sensitive files found")
        return True

def check_hardcoded_credentials():
    """Check for hardcoded credentials in source code."""
    patterns = [
        r'client_id\s*=\s*["\'][^"\']+["\']',
        r'client_secret\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'password\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']'
    ]
    
    # Exclude virtual environment and other directories
    exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache'}
    python_files = []
    
    for file_path in Path('.').rglob('*.py'):
        # Skip files in excluded directories
        if not any(exclude_dir in str(file_path).split(os.sep) for exclude_dir in exclude_dirs):
            python_files.append(file_path)
    
    found_credentials = []
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        found_credentials.append(f"{file_path}: {matches}")
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
    
    if found_credentials:
        print(f"❌ Found potential hardcoded credentials:")
        for cred in found_credentials:
            print(f"   {cred}")
        return False
    else:
        print("✅ No hardcoded credentials found")
        return True

def check_gitignore():
    """Check if sensitive files are properly excluded."""
    gitignore_content = ""
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
    
    required_exclusions = [
        '.env',
        '.streamlit/secrets.toml',
        '__pycache__',
        '*.pyc'
    ]
    
    missing_exclusions = []
    for exclusion in required_exclusions:
        if exclusion not in gitignore_content:
            missing_exclusions.append(exclusion)
    
    if missing_exclusions:
        print(f"❌ Missing .gitignore exclusions: {missing_exclusions}")
        return False
    else:
        print("✅ .gitignore properly configured")
        return True

def check_streamlit_config():
    """Check Streamlit configuration for security settings."""
    config_file = '.streamlit/config.toml'
    if not os.path.exists(config_file):
        print("❌ Streamlit config file not found")
        return False
    
    with open(config_file, 'r') as f:
        config_content = f.read()
    
    security_checks = [
        ('enableXsrfProtection = true', 'XSRF protection'),
        ('developmentMode = false', 'Development mode disabled'),
        ('gatherUsageStats = false', 'Usage stats disabled')
    ]
    
    failed_checks = []
    for check, description in security_checks:
        if check not in config_content:
            failed_checks.append(description)
    
    if failed_checks:
        print(f"❌ Security configuration issues: {failed_checks}")
        return False
    else:
        print("✅ Streamlit security configuration verified")
        return True

def check_dependencies():
    """Check if required files exist."""
    required_files = [
        'main.py',
        'requirements.txt',
        'packages.txt',
        'README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    else:
        print("✅ All required files present")
        return True

def main():
    """Run all security checks."""
    print("🔍 Running security verification for Streamlit deployment...\n")
    
    checks = [
        ("Sensitive Files", check_sensitive_files),
        ("Hardcoded Credentials", check_hardcoded_credentials),
        ("Gitignore Configuration", check_gitignore),
        ("Streamlit Security Config", check_streamlit_config),
        ("Required Files", check_dependencies)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Security Check Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All security checks passed! Ready for deployment.")
        print("\nNext steps:")
        print("1. Go to https://share.streamlit.io/")
        print("2. Click 'New app'")
        print("3. Connect your GitHub repository")
        print("4. Set main file path to 'main.py'")
        print("5. Add your Reddit API credentials in the secrets section")
        print("6. Deploy!")
        return 0
    else:
        print("❌ Security issues found. Please fix them before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
