#!/usr/bin/env python3
"""
Streamlit Deployment Configuration Validator
Validates all configuration files for Streamlit Cloud deployment
"""

import os
import sys
import re
from pathlib import Path

def check_streamlit_config():
    """Check Streamlit configuration file."""
    print("🔧 Checking Streamlit configuration...")
    
    config_file = Path(".streamlit/config.toml")
    if not config_file.exists():
        print("❌ .streamlit/config.toml not found")
        return False
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
        
        # Check critical settings using regex
        checks = [
            (r'developmentMode\s*=\s*false', "Development mode should be disabled"),
            (r'enableXsrfProtection\s*=\s*true', "XSRF protection should be enabled"),
            (r'gatherUsageStats\s*=\s*false', "Usage stats should be disabled"),
            (r'caching\s*=\s*true', "Caching should be enabled")
        ]
        
        all_passed = True
        for pattern, description in checks:
            if re.search(pattern, content, re.IGNORECASE):
                print(f"✅ {description}")
            else:
                print(f"❌ {description}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False

def check_requirements():
    """Check requirements.txt file."""
    print("\n📦 Checking requirements.txt...")
    
    req_file = Path("requirements.txt")
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        with open(req_file, 'r') as f:
            requirements = f.read().strip()
        
        required_packages = [
            "praw",
            "python-dotenv", 
            "pandas",
            "streamlit",
            "plotly"
        ]
        
        missing = []
        for package in required_packages:
            if package not in requirements:
                missing.append(package)
        
        if missing:
            print(f"❌ Missing packages: {missing}")
            return False
        else:
            print("✅ All required packages found")
            return True
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def check_main_file():
    """Check main.py file exists and is valid."""
    print("\n📄 Checking main.py...")
    
    main_file = Path("main.py")
    if not main_file.exists():
        print("❌ main.py not found")
        return False
    
    try:
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check for critical imports
        required_imports = [
            "import streamlit",
            "import praw",
            "import pandas",
            "import plotly"
        ]
        
        missing_imports = []
        for imp in required_imports:
            if imp not in content:
                missing_imports.append(imp)
        
        if missing_imports:
            print(f"❌ Missing imports: {missing_imports}")
            return False
        else:
            print("✅ main.py is valid")
            return True
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False

def check_secrets_template():
    """Check secrets template file."""
    print("\n🔐 Checking secrets template...")
    
    secrets_template = Path(".streamlit/secrets.toml.example")
    if not secrets_template.exists():
        print("❌ .streamlit/secrets.toml.example not found")
        return False
    
    try:
        with open(secrets_template, 'r') as f:
            content = f.read()
        
        required_secrets = [
            "REDDIT_CLIENT_ID",
            "REDDIT_CLIENT_SECRET",
            "REDDIT_USER_AGENT"
        ]
        
        missing_secrets = []
        for secret in required_secrets:
            if secret not in content:
                missing_secrets.append(secret)
        
        if missing_secrets:
            print(f"❌ Missing secrets: {missing_secrets}")
            return False
        else:
            print("✅ Secrets template is complete")
            return True
    except Exception as e:
        print(f"❌ Error reading secrets template: {e}")
        return False

def check_gitignore():
    """Check .gitignore excludes sensitive files."""
    print("\n🚫 Checking .gitignore...")
    
    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        print("❌ .gitignore not found")
        return False
    
    try:
        with open(gitignore_file, 'r') as f:
            content = f.read()
        
        required_exclusions = [
            ".env",
            ".streamlit/secrets.toml",
            "__pycache__",
            "*.pyc"
        ]
        
        missing_exclusions = []
        for exclusion in required_exclusions:
            if exclusion not in content:
                missing_exclusions.append(exclusion)
        
        if missing_exclusions:
            print(f"❌ Missing exclusions: {missing_exclusions}")
            return False
        else:
            print("✅ .gitignore properly configured")
            return True
    except Exception as e:
        print(f"❌ Error reading .gitignore: {e}")
        return False

def main():
    """Main validation function."""
    print("🔍 Streamlit Deployment Configuration Validator")
    print("=" * 50)
    
    checks = [
        ("Streamlit Config", check_streamlit_config),
        ("Requirements", check_requirements),
        ("Main File", check_main_file),
        ("Secrets Template", check_secrets_template),
        ("Gitignore", check_gitignore)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        if check_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All configuration checks passed!")
        print("✅ Ready for Streamlit Cloud deployment")
        print("\nNext steps:")
        print("1. Go to https://share.streamlit.io/")
        print("2. Connect your GitHub repository")
        print("3. Set main file path to 'main.py'")
        print("4. Add your Reddit API credentials in secrets")
        print("5. Deploy!")
        return 0
    else:
        print("❌ Configuration issues found. Please fix them before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
