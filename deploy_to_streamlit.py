#!/usr/bin/env python3
"""
Streamlit Deployment Automation Script
Automates the deployment process to Streamlit Cloud
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met for deployment."""
    print("🔍 Checking deployment prerequisites...")
    
    # Check if git is available
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Git is available")
        else:
            print("❌ Git is not available")
            return False
    except FileNotFoundError:
        print("❌ Git is not installed")
        return False
    
    # Check if repository is clean
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip() == "":
            print("✅ Git repository is clean")
        else:
            print("⚠️  Git repository has uncommitted changes")
            print("   Consider committing changes before deployment")
    except Exception as e:
        print(f"❌ Error checking git status: {e}")
        return False
    
    # Check if remote repository is configured
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Remote repository: {result.stdout.strip()}")
        else:
            print("❌ No remote repository configured")
            return False
    except Exception as e:
        print(f"❌ Error checking remote repository: {e}")
        return False
    
    return True

def push_to_github():
    """Push latest changes to GitHub."""
    print("\n📤 Pushing to GitHub...")
    
    try:
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        print("✅ Changes staged")
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', '🚀 Ready for Streamlit deployment'], check=True)
        print("✅ Changes committed")
        
        # Push to GitHub
        subprocess.run(['git', 'push'], check=True)
        print("✅ Changes pushed to GitHub")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pushing to GitHub: {e}")
        return False

def get_repository_info():
    """Get repository information for deployment."""
    try:
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
        if result.returncode == 0:
            url = result.stdout.strip()
            # Extract repository name from URL
            if 'github.com' in url:
                repo_name = url.split('/')[-1].replace('.git', '')
                return repo_name
        return None
    except Exception:
        return None

def open_streamlit_deployment():
    """Open Streamlit Cloud deployment page."""
    print("\n🌐 Opening Streamlit Cloud deployment page...")
    
    repo_name = get_repository_info()
    if repo_name:
        print(f"📋 Repository: {repo_name}")
    
    # Open Streamlit Cloud
    streamlit_url = "https://share.streamlit.io/"
    print(f"🔗 Opening: {streamlit_url}")
    
    try:
        webbrowser.open(streamlit_url)
        print("✅ Streamlit Cloud page opened in browser")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"   Please manually visit: {streamlit_url}")

def display_deployment_instructions():
    """Display step-by-step deployment instructions."""
    print("\n" + "="*60)
    print("🚀 STREAMLIT CLOUD DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    repo_name = get_repository_info()
    
    print("\n📋 Step-by-Step Instructions:")
    print("1. Sign in to Streamlit Cloud with your GitHub account")
    print("2. Click 'New app'")
    print("3. Configure your app:")
    print(f"   • Repository: {repo_name or 'your-repo-name'}")
    print("   • Branch: main")
    print("   • Main file path: main.py")
    print("   • Python version: 3.8 or higher")
    print("\n4. Click 'Advanced settings' and add your secrets:")
    print("   ```toml")
    print("   REDDIT_CLIENT_ID = \"your_actual_client_id\"")
    print("   REDDIT_CLIENT_SECRET = \"your_actual_client_secret\"")
    print("   REDDIT_USER_AGENT = \"RedditScraper/1.0 by /u/yourusername\"")
    print("   ```")
    print("\n5. Click 'Deploy!'")
    print("\n6. Wait for deployment to complete (2-3 minutes)")
    print("7. Your app will be available at the provided URL")
    
    print("\n" + "="*60)
    print("🔒 SECURITY REMINDER")
    print("="*60)
    print("• Never commit your actual Reddit API credentials")
    print("• Use Streamlit secrets for sensitive data")
    print("• Keep your credentials secure")
    
    print("\n" + "="*60)
    print("📞 SUPPORT")
    print("="*60)
    print("• Check STREAMLIT_DEPLOYMENT.md for detailed instructions")
    print("• Run 'python security_check.py' to verify security")
    print("• Review DEPENDENCY_ANALYSIS.md for compatibility info")

def main():
    """Main deployment automation function."""
    print("🚀 Streamlit Deployment Automation")
    print("="*50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix issues and try again.")
        return 1
    
    # Push to GitHub
    if not push_to_github():
        print("\n❌ Failed to push to GitHub. Please check your git configuration.")
        return 1
    
    # Open Streamlit Cloud
    open_streamlit_deployment()
    
    # Display instructions
    display_deployment_instructions()
    
    print("\n🎉 Deployment setup complete!")
    print("Follow the instructions above to deploy your app to Streamlit Cloud.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
