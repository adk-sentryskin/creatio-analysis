#!/usr/bin/env python3
"""
SentrySkin Data Extractor
Extracts specific fields from the raw SentrySkin execution data
"""

import pandas as pd
import json
import re
from datetime import datetime

def extract_fields_from_raw_data(csv_file):
    """Extract specific fields from the raw data in CSV"""
    print("🔍 Extracting fields from SentrySkin raw data...")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    print(f"📊 Loaded {len(df)} records from CSV")
    
    extracted_data = []
    
    for index, row in df.iterrows():
        try:
            # Basic fields from CSV
            execution_id = row['execution_id']
            timestamp = row['timestamp']
            workflow_status = row['status']
            
            # Parse the raw_data JSON
            raw_data = json.loads(row['raw_data'])
            
            # Initialize extracted fields
            chat_id = ""
            thread_id = ""
            user_agent = ""
            conversation_stage = ""
            workflow_id = "V7n2R2x0bj99pQhK"  # Fixed workflow ID
            
            # Extract from runData
            run_data = raw_data.get('resultData', {}).get('runData', {})
            
            # Look for Webhook data (first node usually contains the main data)
            webhook_data = None
            for node_name, node_data in run_data.items():
                if node_name == 'Webhook' and isinstance(node_data, list) and len(node_data) > 0:
                    webhook_data = node_data[0].get('data', {}).get('main', [[]])
                    if webhook_data and len(webhook_data) > 0 and len(webhook_data[0]) > 0:
                        webhook_data = webhook_data[0][0].get('json', {})
                        break
            
            if webhook_data:
                # Extract user agent from headers
                headers = webhook_data.get('headers', {})
                user_agent = headers.get('user-agent', headers.get('User-Agent', ''))
                
                # Extract chat_id and thread_id from body
                body = webhook_data.get('body', {})
                chat_id = body.get('user_id', '')
                thread_id = body.get('thread_id', '')
            
            # Look for conversation_stage in HTTP Request1 node (response data)
            for node_name, node_data in run_data.items():
                if node_name == 'HTTP Request1' and isinstance(node_data, list) and len(node_data) > 0:
                    response_data = node_data[0].get('data', {}).get('main', [[]])
                    if response_data and len(response_data) > 0 and len(response_data[0]) > 0:
                        response_json = response_data[0][0].get('json', {})
                        conversation_stage = response_json.get('conversation_stage', '')
                        break
            
            # Create extracted record
            extracted_record = {
                'execution_id': execution_id,
                'workflow_id': workflow_id,
                'timestamp': timestamp,
                'user_agent': user_agent,
                'chat_id': chat_id,
                'thread_id': thread_id,
                'conversation_stage': conversation_stage,
                'workflow_status': workflow_status
            }
            
            extracted_data.append(extracted_record)
            
            # Progress indicator
            if (index + 1) % 100 == 0:
                print(f"📈 Processed {index + 1}/{len(df)} records...")
                
        except Exception as e:
            print(f"⚠️ Error processing row {index}: {e}")
            continue
    
    print(f"✅ Successfully extracted data from {len(extracted_data)} records")
    return extracted_data

def save_extracted_data(extracted_data):
    """Save extracted data to files"""
    print("💾 Saving extracted data...")
    
    # Create DataFrame
    df_extracted = pd.DataFrame(extracted_data)
    
    # Save as CSV
    csv_filename = "sentryskin_extracted_fields.csv"
    df_extracted.to_csv(csv_filename, index=False)
    print(f"✅ Extracted data saved to: {csv_filename}")
    
    # Save as JSON
    json_filename = "sentryskin_extracted_fields.json"
    with open(json_filename, 'w') as f:
        json.dump(extracted_data, f, indent=2)
    print(f"✅ Extracted data saved to: {json_filename}")
    
    # Print summary statistics
    print("\n📊 Data Summary:")
    print(f"Total records: {len(extracted_data)}")
    print(f"Records with user_agent: {len([r for r in extracted_data if r['user_agent']])}")
    print(f"Records with chat_id: {len([r for r in extracted_data if r['chat_id']])}")
    print(f"Records with thread_id: {len([r for r in extracted_data if r['thread_id']])}")
    print(f"Records with conversation_stage: {len([r for r in extracted_data if r['conversation_stage']])}")
    
    # Show sample data
    print("\n🔍 Sample Extracted Data:")
    for i, record in enumerate(extracted_data[:3]):
        print(f"\nRecord {i+1}:")
        print(f"  Execution ID: {record['execution_id']}")
        print(f"  Workflow ID: {record['workflow_id']}")
        print(f"  Timestamp: {record['timestamp']}")
        print(f"  User Agent: {record['user_agent'][:100]}..." if len(record['user_agent']) > 100 else f"  User Agent: {record['user_agent']}")
        print(f"  Chat ID: {record['chat_id']}")
        print(f"  Thread ID: {record['thread_id']}")
        print(f"  Conversation Stage: {record['conversation_stage']}")
        print(f"  Workflow Status: {record['workflow_status']}")
    
    return df_extracted

def analyze_user_agents(df):
    """Analyze user agent data"""
    print("\n📱 User Agent Analysis:")
    
    # Filter records with user agents
    user_agent_records = df[df['user_agent'] != '']
    
    if len(user_agent_records) == 0:
        print("❌ No user agent data found")
        return
    
    print(f"📊 Total records with user agents: {len(user_agent_records)}")
    
    # Extract browser/device info
    browsers = {}
    devices = {}
    operating_systems = {}
    
    for user_agent in user_agent_records['user_agent']:
        # Browser detection
        if 'Chrome' in user_agent:
            browsers['Chrome'] = browsers.get('Chrome', 0) + 1
        elif 'Safari' in user_agent and 'Chrome' not in user_agent:
            browsers['Safari'] = browsers.get('Safari', 0) + 1
        elif 'Firefox' in user_agent:
            browsers['Firefox'] = browsers.get('Firefox', 0) + 1
        elif 'Edge' in user_agent:
            browsers['Edge'] = browsers.get('Edge', 0) + 1
        else:
            browsers['Other'] = browsers.get('Other', 0) + 1
        
        # Device detection
        if 'Mobile' in user_agent or 'iPhone' in user_agent or 'Android' in user_agent:
            devices['Mobile'] = devices.get('Mobile', 0) + 1
        elif 'iPad' in user_agent or 'Tablet' in user_agent:
            devices['Tablet'] = devices.get('Tablet', 0) + 1
        else:
            devices['Desktop'] = devices.get('Desktop', 0) + 1
        
        # OS detection
        if 'Windows' in user_agent:
            operating_systems['Windows'] = operating_systems.get('Windows', 0) + 1
        elif 'Mac OS X' in user_agent or 'macOS' in user_agent:
            operating_systems['macOS'] = operating_systems.get('macOS', 0) + 1
        elif 'iPhone' in user_agent or 'iPad' in user_agent:
            operating_systems['iOS'] = operating_systems.get('iOS', 0) + 1
        elif 'Android' in user_agent:
            operating_systems['Android'] = operating_systems.get('Android', 0) + 1
        elif 'Linux' in user_agent:
            operating_systems['Linux'] = operating_systems.get('Linux', 0) + 1
        else:
            operating_systems['Other'] = operating_systems.get('Other', 0) + 1
    
    print("\n🌐 Browser Distribution:")
    for browser, count in sorted(browsers.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(user_agent_records)) * 100
        print(f"  {browser}: {count} ({percentage:.1f}%)")
    
    print("\n📱 Device Distribution:")
    for device, count in sorted(devices.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(user_agent_records)) * 100
        print(f"  {device}: {count} ({percentage:.1f}%)")
    
    print("\n💻 Operating System Distribution:")
    for os, count in sorted(operating_systems.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(user_agent_records)) * 100
        print(f"  {os}: {count} ({percentage:.1f}%)")

def main():
    """Main function"""
    print("🎯 SentrySkin Data Extractor")
    print("=" * 50)
    
    csv_file = "sentryskin_user_agents.csv"
    
    try:
        # Extract fields from raw data
        extracted_data = extract_fields_from_raw_data(csv_file)
        
        if not extracted_data:
            print("❌ No data extracted!")
            return
        
        # Save extracted data
        df_extracted = save_extracted_data(extracted_data)
        
        # Analyze user agents
        analyze_user_agents(df_extracted)
        
        print("\n🎉 Data extraction completed successfully!")
        
    except FileNotFoundError:
        print(f"❌ File not found: {csv_file}")
        print("Please make sure the CSV file exists in the current directory.")
    except Exception as e:
        print(f"❌ Error in main process: {e}")

if __name__ == "__main__":
    main()
