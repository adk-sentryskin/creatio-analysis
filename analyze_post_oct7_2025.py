#!/usr/bin/env python3
"""
SentrySkin User Analysis - Post October 7th, 2025
Analyzes users with interactions after October 7th, 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

def load_and_analyze_data():
    """Load and analyze SentrySkin user data"""
    print("📊 Loading SentrySkin user device analysis data...")
    
    try:
        df = pd.read_csv("sentryskin_user_device_analysis.csv")
        print(f"✅ Loaded {len(df)} user records")
        return df
    except FileNotFoundError:
        print("❌ File 'sentryskin_user_device_analysis.csv' not found!")
        return None

def filter_post_october_7_2025(df):
    """Filter users with interactions after October 7th, 2025"""
    print("\n📅 Filtering users with interactions after October 7th, 2025...")
    
    # Convert timestamp columns to datetime
    df['first_interaction'] = pd.to_datetime(df['first_interaction'], errors='coerce')
    df['last_interaction'] = pd.to_datetime(df['last_interaction'], errors='coerce')
    
    # Define cutoff date
    cutoff_date = pd.to_datetime('2025-10-07', utc=True)
    
    # Filter users whose last interaction is after October 7th, 2025
    post_oct_7_users = df[df['last_interaction'] > cutoff_date]
    
    print(f"📊 Users with interactions after Oct 7th, 2025: {len(post_oct_7_users)}")
    print(f"📊 Total users in dataset: {len(df)}")
    print(f"📊 Percentage: {(len(post_oct_7_users)/len(df))*100:.1f}%")
    
    return post_oct_7_users

def analyze_user_details(post_oct_7_users):
    """Analyze detailed user information"""
    print("\n👥 Detailed User Analysis:")
    
    # Basic statistics
    total_users = len(post_oct_7_users)
    total_conversations = post_oct_7_users['conversation_count'].sum()
    avg_conversations = post_oct_7_users['conversation_count'].mean()
    
    print(f"\n📈 Basic Statistics:")
    print(f"  Total users: {total_users}")
    print(f"  Total conversations: {total_conversations}")
    print(f"  Average conversations per user: {avg_conversations:.1f}")
    print(f"  Max conversations: {post_oct_7_users['conversation_count'].max()}")
    print(f"  Min conversations: {post_oct_7_users['conversation_count'].min()}")
    
    # Device analysis
    print(f"\n📱 Device Analysis:")
    device_counts = {}
    for devices in post_oct_7_users['devices']:
        if pd.notna(devices):
            for device in devices.split(', '):
                device = device.strip()
                device_counts[device] = device_counts.get(device, 0) + 1
    
    for device, count in sorted(device_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_users) * 100
        print(f"  {device}: {count} users ({percentage:.1f}%)")
    
    # Browser analysis
    print(f"\n🌐 Browser Analysis:")
    browser_counts = {}
    for browsers in post_oct_7_users['browsers']:
        if pd.notna(browsers):
            for browser in browsers.split(', '):
                browser = browser.strip()
                browser_counts[browser] = browser_counts.get(browser, 0) + 1
    
    for browser, count in sorted(browser_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_users) * 100
        print(f"  {browser}: {count} users ({percentage:.1f}%)")
    
    # OS analysis
    print(f"\n💻 Operating System Analysis:")
    os_counts = {}
    for os_list in post_oct_7_users['operating_systems']:
        if pd.notna(os_list):
            for os in os_list.split(', '):
                os = os.strip()
                os_counts[os] = os_counts.get(os, 0) + 1
    
    for os, count in sorted(os_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_users) * 100
        print(f"  {os}: {count} users ({percentage:.1f}%)")
    
    return device_counts, browser_counts, os_counts

def create_visualizations(post_oct_7_users, device_counts, browser_counts, os_counts):
    """Create visualizations for the analysis"""
    print("\n📊 Creating visualizations...")
    
    # Set up the plotting style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('SentrySkin Users Analysis - Post October 7th, 2025', fontsize=16, fontweight='bold')
    
    # 1. Device Distribution Pie Chart
    ax1 = axes[0, 0]
    if device_counts:
        devices = list(device_counts.keys())
        counts = list(device_counts.values())
        colors = plt.cm.Set3(range(len(devices)))
        
        wedges, texts, autotexts = ax1.pie(counts, labels=devices, autopct='%1.1f%%', 
                                          colors=colors, startangle=90)
        ax1.set_title('Device Distribution', fontweight='bold')
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_fontweight('bold')
    
    # 2. Browser Distribution Bar Chart
    ax2 = axes[0, 1]
    if browser_counts:
        browsers = list(browser_counts.keys())
        counts = list(browser_counts.values())
        
        bars = ax2.bar(browsers, counts, color=plt.cm.viridis(range(len(browsers))))
        ax2.set_title('Browser Distribution', fontweight='bold')
        ax2.set_ylabel('Number of Users')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    # 3. OS Distribution Bar Chart
    ax3 = axes[1, 0]
    if os_counts:
        os_list = list(os_counts.keys())
        counts = list(os_counts.values())
        
        bars = ax3.bar(os_list, counts, color=plt.cm.plasma(range(len(os_list))))
        ax3.set_title('Operating System Distribution', fontweight='bold')
        ax3.set_ylabel('Number of Users')
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    str(count), ha='center', va='bottom', fontweight='bold')
    
    # 4. Conversation Count Distribution
    ax4 = axes[1, 1]
    conversation_counts = post_oct_7_users['conversation_count']
    
    # Create histogram
    bins = range(1, int(conversation_counts.max()) + 2)
    n, bins, patches = ax4.hist(conversation_counts, bins=bins, alpha=0.7, 
                               color='skyblue', edgecolor='black')
    
    ax4.set_title('Conversation Count Distribution', fontweight='bold')
    ax4.set_xlabel('Number of Conversations')
    ax4.set_ylabel('Number of Users')
    ax4.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = f'Mean: {conversation_counts.mean():.1f}\nMedian: {conversation_counts.median():.1f}\nMax: {conversation_counts.max()}'
    ax4.text(0.7, 0.7, stats_text, transform=ax4.transAxes, 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
             fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('sentryskin_post_oct7_2025_analysis.png', dpi=300, bbox_inches='tight')
    print("✅ Visualization saved as: sentryskin_post_oct7_2025_analysis.png")
    
    return fig

def create_detailed_report(post_oct_7_users):
    """Create a detailed report of users"""
    print("\n📋 Creating detailed user report...")
    
    # Sort by conversation count (descending)
    sorted_users = post_oct_7_users.sort_values('conversation_count', ascending=False)
    
    # Create detailed report
    report_data = []
    
    for idx, user in sorted_users.iterrows():
        report_data.append({
            'user_id': user['user_id'],
            'conversation_count': user['conversation_count'],
            'first_interaction': user['first_interaction'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(user['first_interaction']) else 'N/A',
            'last_interaction': user['last_interaction'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(user['last_interaction']) else 'N/A',
            'devices': user['devices'],
            'browsers': user['browsers'],
            'operating_systems': user['operating_systems'],
            'sample_user_agent': user['sample_user_agent'][:100] + '...' if len(str(user['sample_user_agent'])) > 100 else user['sample_user_agent']
        })
    
    # Save detailed report
    report_df = pd.DataFrame(report_data)
    report_df.to_csv('sentryskin_post_oct7_2025_detailed_report.csv', index=False)
    print("✅ Detailed report saved as: sentryskin_post_oct7_2025_detailed_report.csv")
    
    # Print top 10 most active users
    print(f"\n🏆 Top 10 Most Active Users (Post Oct 7th, 2025):")
    print("-" * 80)
    for i, user in enumerate(sorted_users.head(10).itertuples(), 1):
        print(f"{i:2d}. User ID: {user.user_id}")
        print(f"    Conversations: {user.conversation_count}")
        print(f"    First Interaction: {user.first_interaction.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(user.first_interaction) else 'N/A'}")
        print(f"    Last Interaction: {user.last_interaction.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(user.last_interaction) else 'N/A'}")
        print(f"    Devices: {user.devices}")
        print(f"    Browsers: {user.browsers}")
        print(f"    OS: {user.operating_systems}")
        print("-" * 80)
    
    return report_df

def main():
    """Main analysis function"""
    print("🎯 SentrySkin Users Analysis - Post October 7th, 2025")
    print("=" * 60)
    
    # Load data
    df = load_and_analyze_data()
    if df is None:
        return
    
    # Filter users with interactions after October 7th, 2025
    post_oct_7_users = filter_post_october_7_2025(df)
    
    if len(post_oct_7_users) == 0:
        print("❌ No users found with interactions after October 7th, 2025!")
        return
    
    # Analyze user details
    device_counts, browser_counts, os_counts = analyze_user_details(post_oct_7_users)
    
    # Create visualizations
    fig = create_visualizations(post_oct_7_users, device_counts, browser_counts, os_counts)
    
    # Create detailed report
    report_df = create_detailed_report(post_oct_7_users)
    
    print(f"\n🎉 Analysis completed!")
    print(f"📊 Users with interactions after Oct 7th, 2025: {len(post_oct_7_users)}")
    print(f"📊 Total conversations: {post_oct_7_users['conversation_count'].sum()}")
    print(f"📊 Average conversations per user: {post_oct_7_users['conversation_count'].mean():.1f}")
    print(f"💾 Files generated:")
    print(f"  - sentryskin_post_oct7_2025_analysis.png")
    print(f"  - sentryskin_post_oct7_2025_detailed_report.csv")

if __name__ == "__main__":
    main()
