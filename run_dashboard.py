#!/usr/bin/env python3
"""
🚀 Creatio Lead Analysis Dashboard Launcher
Run this script to start the interactive dashboard
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def run_dashboard():
    """Run the Streamlit dashboard"""
    print("🚀 Starting Creatio Lead Analysis Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🌐 To share with others, use ngrok or deploy to cloud")
    print("🔄 Press Ctrl+C to stop the dashboard")
    print("-" * 60)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

def main():
    print("🎯 Creatio Lead Analysis Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("dashboard.py"):
        print("❌ dashboard.py not found. Please run this script from the project directory.")
        return
    
    # Install requirements
    if not install_requirements():
        return
    
    # Run dashboard
    run_dashboard()

if __name__ == "__main__":
    main()
