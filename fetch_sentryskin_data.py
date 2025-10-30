#!/usr/bin/env python3
"""
SentrySkin Data Fetcher
Fetches execution data from SentrySkin n8n API and extracts user agent details
"""

import requests
import json
import pandas as pd
from datetime import datetime, timezone
import os
import streamlit as st

# Configuration
try:
    API_KEY = st.secrets["SENTRYSKIN_API_KEY"]
except:
    API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhNDEyOWNhNC0zYmUxLTQ1ZDctYmEwNC0wMWVlNzRlNTcyMWMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzYxNjc1NjQ0LCJleHAiOjE3NjQyMTk2MDB9.yJQQGhRG8okOc3pISQ2lBfCIcfZLh4Q9QqTxi29MEtE"  # Replace with your actual API key
BASE_URL = "https://sentryskin.app.n8n.cloud/api/v1/executions"
WORKFLOW_ID = "V7n2R2x0bj99pQhK"
START_DATE = "2024-10-07T00:00:00Z"  # October 7th start date

def fetch_sentryskin_executions():
    """Fetch all SentrySkin executions from n8n API"""
    print("🚀 Fetching SentrySkin execution data...")
    
    cursor = ""
    page = 1
    all_executions = []
    
    while True:
        params = {
            "includeData": "true",
            "status": "success",
            "workflowId": WORKFLOW_ID,
            "limit": 100
        }
        if cursor:
            params["cursor"] = cursor

        try:
            res = requests.get(BASE_URL, headers={"X-N8N-API-KEY": API_KEY}, params=params)
            res.raise_for_status()
            data = res.json()

            executions = data.get("data", [])
            all_executions.extend(executions)
            print(f"📄 Fetched page {page}, total so far: {len(all_executions)}")

            cursor = data.get("nextCursor")
            if not cursor:
                break
            page += 1
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching data: {e}")
            break
    
    print(f"✅ Total executions fetched: {len(all_executions)}")
    return all_executions

def filter_by_date(executions, start_date):
    """Filter executions by start date"""
    print(f"📅 Filtering executions from {start_date}...")
    
    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    filtered_executions = []
    
    for execution in executions:
        try:
            # Parse execution timestamp
            exec_time = execution.get('startedAt', '')
            if exec_time:
                exec_dt = datetime.fromisoformat(exec_time.replace('Z', '+00:00'))
                if exec_dt >= start_dt:
                    filtered_executions.append(execution)
        except Exception as e:
            print(f"⚠️ Error parsing date for execution {execution.get('id', 'unknown')}: {e}")
            continue
    
    print(f"📊 Executions after {start_date}: {len(filtered_executions)}")
    return filtered_executions

def extract_user_agent_data(executions):
    """Extract user agent and related data from executions"""
    print("🔍 Extracting user agent and metadata...")
    
    extracted_data = []
    
    for execution in executions:
        try:
            execution_id = execution.get('id', '')
            started_at = execution.get('startedAt', '')
            finished_at = execution.get('finishedAt', '')
            
            # Get execution data
            execution_data = execution.get('data', {})
            
            # Extract user agent and metadata from execution data
            user_agent = ""
            chat_id = ""
            thread_id = ""
            timestamp = started_at
            
            # Look for user agent in different possible locations
            if isinstance(execution_data, dict):
                # Check for user agent in headers or data
                if 'headers' in execution_data:
                    headers = execution_data['headers']
                    if isinstance(headers, dict):
                        user_agent = headers.get('user-agent', headers.get('User-Agent', ''))
                
                # Check for chat/thread IDs
                chat_id = execution_data.get('chatId', execution_data.get('chat_id', ''))
                thread_id = execution_data.get('threadId', execution_data.get('thread_id', ''))
                
                # Look deeper in the data structure
                if 'data' in execution_data:
                    inner_data = execution_data['data']
                    if isinstance(inner_data, dict):
                        user_agent = user_agent or inner_data.get('userAgent', inner_data.get('user_agent', ''))
                        chat_id = chat_id or inner_data.get('chatId', inner_data.get('chat_id', ''))
                        thread_id = thread_id or inner_data.get('threadId', inner_data.get('thread_id', ''))
            
            # Extract additional metadata
            metadata = {
                'execution_id': execution_id,
                'timestamp': timestamp,
                'finished_at': finished_at,
                'user_agent': user_agent,
                'chat_id': chat_id,
                'thread_id': thread_id,
                'status': execution.get('status', ''),
                'mode': execution.get('mode', ''),
                'raw_data': json.dumps(execution_data) if execution_data else ''
            }
            
            extracted_data.append(metadata)
            
        except Exception as e:
            print(f"⚠️ Error processing execution {execution.get('id', 'unknown')}: {e}")
            continue
    
    print(f"📋 Extracted data for {len(extracted_data)} executions")
    return extracted_data

def save_data(executions, extracted_data):
    """Save raw and processed data to files"""
    print("💾 Saving data to files...")
    
    # Save raw executions
    with open("sentryskin_executions_raw.json", "w") as f:
        json.dump(executions, f, indent=2)
    print("✅ Raw executions saved to: sentryskin_executions_raw.json")
    
    # Save extracted data as JSON
    with open("sentryskin_user_agents.json", "w") as f:
        json.dump(extracted_data, f, indent=2)
    print("✅ User agent data saved to: sentryskin_user_agents.json")
    
    # Save extracted data as CSV
    if extracted_data:
        df = pd.DataFrame(extracted_data)
        df.to_csv("sentryskin_user_agents.csv", index=False)
        print("✅ User agent data saved to: sentryskin_user_agents.csv")
        
        # Print summary
        print("\n📊 Data Summary:")
        print(f"Total executions: {len(extracted_data)}")
        print(f"With user agent: {len([d for d in extracted_data if d['user_agent']])}")
        print(f"With chat ID: {len([d for d in extracted_data if d['chat_id']])}")
        print(f"With thread ID: {len([d for d in extracted_data if d['thread_id']])}")
        
        # Show sample data
        print("\n🔍 Sample Data:")
        for i, data in enumerate(extracted_data[:3]):
            print(f"\nExecution {i+1}:")
            print(f"  ID: {data['execution_id']}")
            print(f"  Timestamp: {data['timestamp']}")
            print(f"  User Agent: {data['user_agent'][:100]}..." if len(data['user_agent']) > 100 else f"  User Agent: {data['user_agent']}")
            print(f"  Chat ID: {data['chat_id']}")
            print(f"  Thread ID: {data['thread_id']}")

def main():
    """Main function to orchestrate the data fetching process"""
    print("🎯 SentrySkin Data Fetcher")
    print("=" * 50)
    
    # Check if API key is set
    if API_KEY == "YOUR_API_KEY":
        print("❌ Please set your API_KEY in the script before running!")
        return
    
    try:
        # Fetch all executions
        all_executions = fetch_sentryskin_executions()
        
        if not all_executions:
            print("❌ No executions found!")
            return
        
        # Filter by date
        filtered_executions = filter_by_date(all_executions, START_DATE)
        
        if not filtered_executions:
            print(f"❌ No executions found after {START_DATE}!")
            return
        
        # Extract user agent data
        extracted_data = extract_user_agent_data(filtered_executions)
        
        # Save data
        save_data(filtered_executions, extracted_data)
        
        print("\n🎉 Data fetching completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in main process: {e}")

if __name__ == "__main__":
    main()
