#!/usr/bin/env python3
"""
Deployment Readiness Checker
Checks if your project is ready for cloud deployment
"""

import os
import sys

def check_file_exists(filepath, required=True):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "(required)" if required else "(optional)"
    print(f"{status} {filepath} {req_text}")
    return exists

def check_requirements():
    """Check requirements files"""
    print("\n📦 Requirements Files:")
    print("-" * 50)
    
    has_deploy = check_file_exists("requirements-deploy.txt", required=True)
    check_file_exists("requirements-light.txt", required=False)
    check_file_exists("packages.txt", required=True)
    check_file_exists("apt.txt", required=False)
    
    return has_deploy

def check_config():
    """Check configuration files"""
    print("\n⚙️  Configuration Files:")
    print("-" * 50)
    
    check_file_exists(".streamlit/config.toml", required=False)
    check_file_exists("Procfile", required=False)
    check_file_exists("runtime.txt", required=False)
    
    return True

def check_main_files():
    """Check main application files"""
    print("\n🎯 Main Application Files:")
    print("-" * 50)
    
    has_main = check_file_exists("pro_interview_system.py", required=True)
    check_file_exists("interview_monitor.py", required=False)
    check_file_exists("app_web.py", required=False)
    
    return has_main

def check_docker():
    """Check Docker files"""
    print("\n🐳 Docker Files:")
    print("-" * 50)
    
    check_file_exists("backend/Dockerfile", required=False)
    check_file_exists("backend/requirements.txt", required=False)
    check_file_exists("microservice/Dockerfile", required=False)
    check_file_exists("microservice/docker-compose.yml", required=False)
    
    return True

def analyze_requirements(filepath):
    """Analyze requirements file"""
    if not os.path.exists(filepath):
        return False
    
    print(f"\n🔍 Analyzing {filepath}:")
    print("-" * 50)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check for problematic packages
    issues = []
    if 'dlib' in content:
        issues.append("⚠️  Contains 'dlib' - requires CMake (may fail on cloud)")
    if 'PyQt5' in content:
        issues.append("⚠️  Contains 'PyQt5' - not needed for web deployment")
    if 'opencv-python>=' in content and 'headless' not in content:
        issues.append("💡 Consider using 'opencv-python-headless' for cloud")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✅ No deployment issues detected")
    
    # Count packages
    lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
    print(f"📊 Total packages: {len(lines)}")
    
    return len(issues) == 0

def get_deployment_recommendation():
    """Provide deployment recommendation"""
    print("\n🎯 Deployment Recommendations:")
    print("=" * 50)
    
    if os.path.exists("requirements-deploy.txt"):
        print("✅ READY FOR CLOUD DEPLOYMENT")
        print("\nRecommended platforms:")
        print("  1. Streamlit Cloud (easiest)")
        print("  2. Render (full features)")
        print("  3. Railway (Docker support)")
        print("\nNext steps:")
        print("  1. Rename requirements-deploy.txt to requirements.txt")
        print("  2. Commit and push to GitHub")
        print("  3. Deploy on your chosen platform")
    else:
        print("⚠️  DEPLOYMENT FILES MISSING")
        print("\nRun this to create deployment files:")
        print("  ./switch_deploy_mode.sh")
    
    if os.path.exists("backend/Dockerfile"):
        print("\n🐳 Docker deployment available:")
        print("  cd backend && docker build -t app . && docker run -p 8000:8000 app")

def main():
    """Main checker function"""
    print("=" * 50)
    print("🚀 DEPLOYMENT READINESS CHECKER")
    print("=" * 50)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run checks
    has_deploy = check_requirements()
    has_config = check_config()
    has_main = check_main_files()
    check_docker()
    
    # Analyze requirements
    if os.path.exists("requirements.txt"):
        analyze_requirements("requirements.txt")
    
    if os.path.exists("requirements-deploy.txt"):
        analyze_requirements("requirements-deploy.txt")
    
    # Overall status
    print("\n" + "=" * 50)
    if has_deploy and has_main:
        print("✅ PROJECT IS READY FOR DEPLOYMENT!")
    else:
        print("❌ PROJECT NEEDS SETUP")
        print("\nMissing required files. Run:")
        print("  ./switch_deploy_mode.sh")
    print("=" * 50)
    
    # Recommendations
    get_deployment_recommendation()
    
    print("\n📚 For detailed instructions, see:")
    print("  - DEPLOYMENT_SOLUTION.md (quick fix)")
    print("  - DEPLOY_INSTRUCTIONS.md (full guide)")
    print("  - DEPLOYMENT_FIX.md (technical details)")
    print()

if __name__ == "__main__":
    main()
