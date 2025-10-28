#!/usr/bin/env python3
"""
Automated Pipeline for Creatio Lead Analysis Dashboard
======================================================

This script automates the entire data pipeline:
1. Fetch Creatio leads data
2. Fetch SentrySkin n8n execution data
3. Extract and process SentrySkin fields
4. Analyze user device patterns
5. Generate post-October 7th analysis
6. Launch the dashboard

Usage:
    python automate_pipeline.py [--skip-fetch] [--skip-analysis] [--dashboard-only]
"""

import os
import sys
import subprocess
import argparse
import time
from datetime import datetime
import pandas as pd

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_step(step_num, total_steps, description):
    """Print a formatted step"""
    print(f"\n📋 Step {step_num}/{total_steps}: {description}")
    print("-" * 50)

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    print(f"🔄 Running {description}...")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print("📊 Output:", result.stdout[-200:])  # Show last 200 chars
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error in {description}:")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ Script {script_name} not found")
        return False

def check_file_exists(filename, description):
    """Check if a file exists"""
    if os.path.exists(filename):
        print(f"✅ {description} exists: {filename}")
        return True
    else:
        print(f"❌ {description} missing: {filename}")
        return False

def get_file_size(filename):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(filename)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    except:
        return "Unknown"

def main():
    parser = argparse.ArgumentParser(description='Automated Creatio Analysis Pipeline')
    parser.add_argument('--skip-fetch', action='store_true', 
                       help='Skip data fetching steps')
    parser.add_argument('--skip-analysis', action='store_true', 
                       help='Skip analysis steps')
    parser.add_argument('--dashboard-only', action='store_true', 
                       help='Only launch dashboard (skip all processing)')
    parser.add_argument('--port', type=int, default=8501, 
                       help='Dashboard port (default: 8501)')
    
    args = parser.parse_args()
    
    print_header("CREATIO LEAD ANALYSIS - AUTOMATED PIPELINE")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define pipeline steps
    pipeline_steps = [
        ("fetch_leads.py", "Fetch Creatio Leads Data"),
        ("fetch_sentryskin_data.py", "Fetch SentrySkin n8n Data"),
        ("extract_sentryskin_fields.py", "Extract SentrySkin Fields"),
        ("analyze_sentryskin_users.py", "Analyze User Device Patterns"),
        ("analyze_post_oct7_2025.py", "Generate Post-Oct 7th Analysis")
    ]
    
    total_steps = len(pipeline_steps) + 1  # +1 for dashboard launch
    
    # Check if we should skip processing
    if args.dashboard_only:
        print("\n🎯 Dashboard-only mode: Skipping all data processing")
        skip_to_dashboard = True
    elif args.skip_fetch and args.skip_analysis:
        print("\n🎯 Skipping all processing steps")
        skip_to_dashboard = True
    else:
        skip_to_dashboard = False
    
    # Run data processing pipeline
    if not skip_to_dashboard:
        print("\n📊 DATA PROCESSING PIPELINE")
        
        for i, (script, description) in enumerate(pipeline_steps, 1):
            if args.skip_fetch and i <= 2:  # Skip first 2 steps (fetching)
                print(f"\n⏭️  Skipping {description} (--skip-fetch)")
                continue
            if args.skip_analysis and i > 2:  # Skip last 3 steps (analysis)
                print(f"\n⏭️  Skipping {description} (--skip-analysis)")
                continue
                
            print_step(i, total_steps, description)
            success = run_script(script, description)
            if not success:
                print(f"\n❌ Pipeline failed at step {i}: {description}")
                print("🛑 Stopping pipeline. Check the error above.")
                return False
    
    # Verify essential files exist
    print("\n🔍 VERIFYING ESSENTIAL FILES")
    essential_files = [
        ("leads_export.csv", "Creatio Leads Data"),
        ("sentryskin_user_agents.csv", "SentrySkin Raw Data"),
        ("sentryskin_extracted_fields.csv", "SentrySkin Extracted Fields"),
        ("sentryskin_user_device_analysis.csv", "User Device Analysis"),
        ("sentryskin_post_oct7_2025_detailed_report.csv", "Post-Oct 7th Analysis"),
        ("dashboard.py", "Dashboard Application"),
        ("requirements.txt", "Dependencies")
    ]
    
    missing_files = []
    for filename, description in essential_files:
        if not check_file_exists(filename, description):
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n❌ Missing essential files: {', '.join(missing_files)}")
        print("🛑 Cannot proceed without these files.")
        return False
    
    # Show file sizes
    print("\n📁 FILE SIZES")
    for filename, description in essential_files:
        if os.path.exists(filename):
            size = get_file_size(filename)
            print(f"  {filename}: {size}")
    
    # Launch dashboard
    print_step(total_steps, total_steps, "Launch Dashboard")
    print(f"🌐 Starting dashboard on port {args.port}...")
    print(f"📱 Dashboard will be available at: http://localhost:{args.port}")
    print(f"🌍 Network access: http://10.106.6.133:{args.port}")
    print("\n" + "="*60)
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n💡 Tips:")
    print("  • Use Ctrl+C to stop the dashboard")
    print("  • Refresh the browser to see updated data")
    print("  • Check the terminal for any error messages")
    print("\n🚀 Launching dashboard...")
    
    try:
        # Launch Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", str(args.port),
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
        print("✅ Pipeline completed successfully")
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
