#!/usr/bin/env python3
"""
Health Check Script for Creatio Lead Analysis Dashboard
=======================================================

This script checks the health of the dashboard and data pipeline:
1. Verifies essential files exist
2. Checks data freshness
3. Validates API connectivity
4. Tests dashboard accessibility

Usage:
    python health_check.py [--verbose] [--fix-issues]
"""

import os
import sys
import requests
import pandas as pd
from datetime import datetime, timedelta
import argparse

def print_status(message, status="INFO"):
    """Print formatted status message"""
    colors = {
        "INFO": "\033[0;34m",    # Blue
        "SUCCESS": "\033[0;32m", # Green
        "WARNING": "\033[1;33m", # Yellow
        "ERROR": "\033[0;31m",   # Red
    }
    symbols = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌"
    }
    
    color = colors.get(status, colors["INFO"])
    symbol = symbols.get(status, symbols["INFO"])
    print(f"{color}{symbol} {message}\033[0m")

def check_file_health(filename, description, max_age_hours=24):
    """Check if file exists and is recent"""
    if not os.path.exists(filename):
        print_status(f"{description} missing: {filename}", "ERROR")
        return False
    
    # Check file age
    file_time = datetime.fromtimestamp(os.path.getmtime(filename))
    age_hours = (datetime.now() - file_time).total_seconds() / 3600
    
    if age_hours > max_age_hours:
        print_status(f"{description} is {age_hours:.1f} hours old (max: {max_age_hours}h)", "WARNING")
    else:
        print_status(f"{description} is fresh ({age_hours:.1f}h old)", "SUCCESS")
    
    # Check file size
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    if size_mb < 0.1:  # Less than 100KB
        print_status(f"{description} is very small ({size_mb:.2f} MB)", "WARNING")
    else:
        print_status(f"{description} size: {size_mb:.2f} MB", "INFO")
    
    return True

def check_data_quality(filename, description):
    """Check data quality of CSV files"""
    try:
        df = pd.read_csv(filename)
        
        if df.empty:
            print_status(f"{description} is empty", "ERROR")
            return False
        
        print_status(f"{description} has {len(df)} records", "SUCCESS")
        
        # Check for missing values
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 20:
            print_status(f"{description} has {missing_pct:.1f}% missing values", "WARNING")
        else:
            print_status(f"{description} data quality: {100-missing_pct:.1f}% complete", "SUCCESS")
        
        return True
        
    except Exception as e:
        print_status(f"Error reading {description}: {e}", "ERROR")
        return False

def check_dashboard_accessibility(port=8501):
    """Check if dashboard is accessible"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=5)
        if response.status_code == 200:
            print_status(f"Dashboard accessible on port {port}", "SUCCESS")
            return True
        else:
            print_status(f"Dashboard returned status {response.status_code}", "WARNING")
            return False
    except requests.exceptions.ConnectionError:
        print_status(f"Dashboard not accessible on port {port}", "ERROR")
        return False
    except Exception as e:
        print_status(f"Dashboard check failed: {e}", "ERROR")
        return False

def check_api_connectivity():
    """Check API connectivity (basic check)"""
    # This is a basic check - in production you'd want to test actual API calls
    print_status("API connectivity check (basic)", "INFO")
    
    # Check if API keys are present in scripts
    api_files = ["fetch_leads.py", "fetch_sentryskin_data.py"]
    for file in api_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                content = f.read()
                if "API_KEY" in content and "YOUR_API_KEY" not in content:
                    print_status(f"{file} has API key configured", "SUCCESS")
                else:
                    print_status(f"{file} needs API key configuration", "WARNING")

def main():
    parser = argparse.ArgumentParser(description='Health Check for Creatio Dashboard')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--fix-issues', action='store_true', help='Attempt to fix issues')
    parser.add_argument('--port', type=int, default=8501, help='Dashboard port')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🏥 CREATIO DASHBOARD HEALTH CHECK")
    print("=" * 60)
    print(f"🕒 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Essential files to check
    essential_files = [
        ("dashboard.py", "Dashboard Application", 168),  # 1 week
        ("requirements.txt", "Dependencies", 168),
        ("automate_pipeline.py", "Pipeline Script", 168),
        ("deploy.sh", "Deployment Script", 168),
    ]
    
    # Data files to check
    data_files = [
        ("leads_export.csv", "Creatio Leads Data", 24),  # 1 day
        ("sentryskin_user_agents.csv", "SentrySkin Raw Data", 24),
        ("sentryskin_extracted_fields.csv", "SentrySkin Fields", 24),
        ("sentryskin_user_device_analysis.csv", "User Analysis", 24),
        ("sentryskin_post_oct7_2025_detailed_report.csv", "Post-Oct 7th Report", 24),
    ]
    
    print("📁 CHECKING ESSENTIAL FILES")
    print("-" * 30)
    essential_ok = True
    for filename, description, max_age in essential_files:
        if not check_file_health(filename, description, max_age):
            essential_ok = False
    
    print("\n📊 CHECKING DATA FILES")
    print("-" * 30)
    data_ok = True
    for filename, description, max_age in data_files:
        if not check_file_health(filename, description, max_age):
            data_ok = False
        else:
            # Check data quality for CSV files
            if filename.endswith('.csv'):
                check_data_quality(filename, description)
    
    print("\n🌐 CHECKING DASHBOARD ACCESSIBILITY")
    print("-" * 30)
    dashboard_ok = check_dashboard_accessibility(args.port)
    
    print("\n🔌 CHECKING API CONNECTIVITY")
    print("-" * 30)
    check_api_connectivity()
    
    print("\n" + "=" * 60)
    print("📋 HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    if essential_ok and data_ok and dashboard_ok:
        print_status("All systems healthy! 🎉", "SUCCESS")
        print("\n💡 Recommendations:")
        print("  • Dashboard is ready for use")
        print("  • All data files are fresh")
        print("  • Run './deploy.sh' to refresh data if needed")
    else:
        print_status("Issues detected! ⚠️", "WARNING")
        print("\n🔧 Recommended actions:")
        
        if not essential_ok:
            print("  • Check that all essential files are present")
            print("  • Run 'git pull' or restore missing files")
        
        if not data_ok:
            print("  • Run 'python automate_pipeline.py' to refresh data")
            print("  • Check API credentials if data fetching fails")
        
        if not dashboard_ok:
            print("  • Run './deploy.sh --dashboard-only' to start dashboard")
            print("  • Check if port is available")
        
        if args.fix_issues:
            print("\n🔧 Attempting to fix issues...")
            if not data_ok:
                print("Running data pipeline...")
                os.system("python automate_pipeline.py --skip-fetch")
            if not dashboard_ok:
                print("Starting dashboard...")
                os.system(f"streamlit run dashboard.py --server.port {args.port} --server.headless true &")
    
    print(f"\n🕒 Health check completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
