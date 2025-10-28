#!/usr/bin/env python3
"""
SentrySkin User Analysis
Analyzes unique users and their device patterns from October 7th onwards
"""

import pandas as pd
import json
from datetime import datetime
import re
from collections import defaultdict

def load_extracted_data():
    """Load the extracted SentrySkin data"""
    print("📊 Loading extracted SentrySkin data...")
    
    try:
        df = pd.read_csv("sentryskin_extracted_fields.csv")
        print(f"✅ Loaded {len(df)} records")
        return df
    except FileNotFoundError:
        print("❌ File 'sentryskin_extracted_fields.csv' not found!")
        print("Please run extract_sentryskin_fields.py first to generate the data.")
        return None

def filter_by_date(df, start_date="2024-10-07"):
    """Filter data from October 7th onwards"""
    print(f"📅 Filtering data from {start_date} onwards...")
    
    # Convert timestamp to datetime with UTC timezone
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    
    # Filter by date - make sure start_dt is also timezone-aware
    start_dt = pd.to_datetime(start_date, utc=True)
    filtered_df = df[df['timestamp'] >= start_dt]
    
    print(f"📊 Records from {start_date} onwards: {len(filtered_df)}")
    return filtered_df

def analyze_unique_users(df):
    """Analyze unique users based on chat_id and thread_id"""
    print("\n👥 Analyzing unique users...")
    
    # Create user identifier (prefer chat_id, fallback to thread_id)
    df['user_identifier'] = df['chat_id'].fillna(df['thread_id'])
    
    # Remove empty user identifiers
    df_with_users = df[df['user_identifier'] != '']
    
    print(f"📊 Records with user identifiers: {len(df_with_users)}")
    
    # Get unique users
    unique_users = df_with_users['user_identifier'].unique()
    print(f"👤 Total unique users: {len(unique_users)}")
    
    # Count conversations per user
    user_conversation_counts = df_with_users['user_identifier'].value_counts()
    
    print(f"\n📈 Conversation Distribution:")
    print(f"  Users with 1 conversation: {len(user_conversation_counts[user_conversation_counts == 1])}")
    print(f"  Users with 2-5 conversations: {len(user_conversation_counts[(user_conversation_counts >= 2) & (user_conversation_counts <= 5)])}")
    print(f"  Users with 6-10 conversations: {len(user_conversation_counts[(user_conversation_counts >= 6) & (user_conversation_counts <= 10)])}")
    print(f"  Users with 10+ conversations: {len(user_conversation_counts[user_conversation_counts > 10])}")
    
    return df_with_users, unique_users, user_conversation_counts

def analyze_user_devices(df_with_users):
    """Analyze device patterns for each unique user"""
    print("\n📱 Analyzing user device patterns...")
    
    # Group by user and get their device information
    user_devices = {}
    
    for user_id in df_with_users['user_identifier'].unique():
        user_records = df_with_users[df_with_users['user_identifier'] == user_id]
        
        # Get unique user agents for this user
        user_agents = user_records['user_agent'].dropna().unique()
        
        # Get timestamp information
        timestamps = user_records['timestamp'].tolist()
        first_interaction = min(timestamps) if timestamps else None
        last_interaction = max(timestamps) if timestamps else None
        
        # Analyze each user agent
        devices = []
        browsers = []
        operating_systems = []
        
        for user_agent in user_agents:
            if user_agent:
                # Device detection
                if 'Mobile' in user_agent or 'iPhone' in user_agent or 'Android' in user_agent:
                    devices.append('Mobile')
                elif 'iPad' in user_agent or 'Tablet' in user_agent:
                    devices.append('Tablet')
                else:
                    devices.append('Desktop')
                
                # Browser detection
                if 'Chrome' in user_agent:
                    browsers.append('Chrome')
                elif 'Safari' in user_agent and 'Chrome' not in user_agent:
                    browsers.append('Safari')
                elif 'Firefox' in user_agent:
                    browsers.append('Firefox')
                elif 'Edge' in user_agent:
                    browsers.append('Edge')
                else:
                    browsers.append('Other')
                
                # OS detection
                if 'Windows' in user_agent:
                    operating_systems.append('Windows')
                elif 'Mac OS X' in user_agent or 'macOS' in user_agent:
                    operating_systems.append('macOS')
                elif 'iPhone' in user_agent or 'iPad' in user_agent:
                    operating_systems.append('iOS')
                elif 'Android' in user_agent:
                    operating_systems.append('Android')
                elif 'Linux' in user_agent:
                    operating_systems.append('Linux')
                else:
                    operating_systems.append('Other')
        
        user_devices[user_id] = {
            'conversation_count': len(user_records),
            'unique_devices': list(set(devices)),
            'unique_browsers': list(set(browsers)),
            'unique_operating_systems': list(set(operating_systems)),
            'user_agents': list(user_agents),
            'first_interaction': first_interaction,
            'last_interaction': last_interaction,
            'all_timestamps': timestamps
        }
    
    return user_devices

def generate_device_statistics(user_devices):
    """Generate comprehensive device statistics"""
    print("\n📊 Device Statistics Summary:")
    
    # Overall device distribution
    device_counts = defaultdict(int)
    browser_counts = defaultdict(int)
    os_counts = defaultdict(int)
    
    # Multi-device users
    multi_device_users = 0
    multi_browser_users = 0
    multi_os_users = 0
    
    for user_id, data in user_devices.items():
        # Count devices
        for device in data['unique_devices']:
            device_counts[device] += 1
        
        # Count browsers
        for browser in data['unique_browsers']:
            browser_counts[browser] += 1
        
        # Count operating systems
        for os in data['unique_operating_systems']:
            os_counts[os] += 1
        
        # Count multi-device users
        if len(data['unique_devices']) > 1:
            multi_device_users += 1
        if len(data['unique_browsers']) > 1:
            multi_browser_users += 1
        if len(data['unique_operating_systems']) > 1:
            multi_os_users += 1
    
    total_users = len(user_devices)
    
    print(f"\n📱 Device Distribution (by unique users):")
    for device, count in sorted(device_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_users) * 100
        print(f"  {device}: {count} users ({percentage:.1f}%)")
    
    print(f"\n🌐 Browser Distribution (by unique users):")
    for browser, count in sorted(browser_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_users) * 100
        print(f"  {browser}: {count} users ({percentage:.1f}%)")
    
    print(f"\n💻 Operating System Distribution (by unique users):")
    for os, count in sorted(os_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_users) * 100
        print(f"  {os}: {count} users ({percentage:.1f}%)")
    
    print(f"\n🔄 Multi-Device Usage:")
    print(f"  Users with multiple devices: {multi_device_users} ({(multi_device_users/total_users)*100:.1f}%)")
    print(f"  Users with multiple browsers: {multi_browser_users} ({(multi_browser_users/total_users)*100:.1f}%)")
    print(f"  Users with multiple OS: {multi_os_users} ({(multi_os_users/total_users)*100:.1f}%)")
    
    return device_counts, browser_counts, os_counts

def analyze_conversation_patterns(user_devices):
    """Analyze conversation patterns by device type"""
    print("\n💬 Conversation Patterns by Device:")
    
    # Group users by their primary device
    device_groups = defaultdict(list)
    
    for user_id, data in user_devices.items():
        if data['unique_devices']:
            # Use the first device as primary (most common)
            primary_device = data['unique_devices'][0]
            device_groups[primary_device].append(data['conversation_count'])
    
    for device, conversation_counts in device_groups.items():
        avg_conversations = sum(conversation_counts) / len(conversation_counts)
        max_conversations = max(conversation_counts)
        min_conversations = min(conversation_counts)
        
        print(f"\n  {device} Users:")
        print(f"    Total users: {len(conversation_counts)}")
        print(f"    Average conversations per user: {avg_conversations:.1f}")
        print(f"    Max conversations: {max_conversations}")
        print(f"    Min conversations: {min_conversations}")

def save_detailed_analysis(user_devices):
    """Save detailed analysis to files"""
    print("\n💾 Saving detailed analysis...")
    
    # Create detailed user analysis
    detailed_analysis = []
    
    for user_id, data in user_devices.items():
        # Convert timestamps to strings for CSV
        first_interaction_str = data['first_interaction'].strftime('%Y-%m-%d %H:%M:%S UTC') if data['first_interaction'] else ''
        last_interaction_str = data['last_interaction'].strftime('%Y-%m-%d %H:%M:%S UTC') if data['last_interaction'] else ''
        
        detailed_analysis.append({
            'user_id': user_id,
            'conversation_count': data['conversation_count'],
            'first_interaction': first_interaction_str,
            'last_interaction': last_interaction_str,
            'devices': ', '.join(data['unique_devices']),
            'browsers': ', '.join(data['unique_browsers']),
            'operating_systems': ', '.join(data['unique_operating_systems']),
            'device_count': len(data['unique_devices']),
            'browser_count': len(data['unique_browsers']),
            'os_count': len(data['unique_operating_systems']),
            'sample_user_agent': data['user_agents'][0] if data['user_agents'] else ''
        })
    
    # Save as CSV
    df_analysis = pd.DataFrame(detailed_analysis)
    df_analysis.to_csv("sentryskin_user_device_analysis.csv", index=False)
    print("✅ Detailed analysis saved to: sentryskin_user_device_analysis.csv")
    
    # Save as JSON
    with open("sentryskin_user_device_analysis.json", 'w') as f:
        json.dump(user_devices, f, indent=2, default=str)
    print("✅ Detailed analysis saved to: sentryskin_user_device_analysis.json")
    
    return df_analysis

def main():
    """Main analysis function"""
    print("🎯 SentrySkin User Device Analysis")
    print("=" * 50)
    
    # Load data
    df = load_extracted_data()
    if df is None:
        return
    
    # Filter by date (October 7th onwards)
    df_filtered = filter_by_date(df)
    
    if len(df_filtered) == 0:
        print("❌ No data found from October 7th onwards!")
        return
    
    # Analyze unique users
    df_with_users, unique_users, conversation_counts = analyze_unique_users(df_filtered)
    
    # Analyze user devices
    user_devices = analyze_user_devices(df_with_users)
    
    # Generate statistics
    device_counts, browser_counts, os_counts = generate_device_statistics(user_devices)
    
    # Analyze conversation patterns
    analyze_conversation_patterns(user_devices)
    
    # Save detailed analysis
    df_analysis = save_detailed_analysis(user_devices)
    
    print(f"\n🎉 Analysis completed!")
    print(f"📊 Total unique users analyzed: {len(unique_users)}")
    print(f"📅 Data period: October 7th onwards")
    print(f"💾 Results saved to CSV and JSON files")

if __name__ == "__main__":
    main()
