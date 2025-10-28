import requests
import json
import pandas as pd
from datetime import datetime

# ==============================
# 🔐 CONFIGURATION
# ==============================
TOKEN_URL = "https://christinevalmy-is.creatio.com/connect/token"
ODATA_URL = "https://christinevalmy.creatio.com/0/odata/Lead"
CLIENT_ID = "4D8E6F5A8AC8F7BB66EA1A3DC60AE5BC"
CLIENT_SECRET = "86F4E90DA7949169E5E81E3D743E49F08B088BBD5E76709EAAB17FBE42814201"

# Replace with your actual RegisterMethod GUID
REGISTER_METHOD_GUID = "7928af33-a08e-443f-b949-4ba4ab251617"

# ==============================
# 🗺️ GUID MAPPINGS
# ==============================
LANGUAGE_MAPPING = {
    "b0ecb42d-e1ec-4f1c-bc67-21d2879a3e89": "Spanish",
    "9d2a6c95-d6b6-4326-94d7-1a33cda7294f": "English"
}

LOCATION_MAPPING = {
    "b7c76209-510b-4bce-8992-b58fdedeedb9": "New Jersey",
    "7c071a2e-c0ab-44fa-8d36-3d74b996771b": "New York"
}

REGISTER_METHOD_MAPPING = {
    "240ab9c6-4d7c-4688-b380-af44dd147d7a": "Added manually",
    "2f65913c-ff62-40fb-9d01-1a3e2e893e0e": "Created automatically",
    "7928af33-a08e-443f-b949-4ba4ab251617": "sentryskin",
    "85275068-7b5b-424b-ac4d-f7050aee1eef": "Case",
    "95310edf-2f03-4a9e-babd-24f1de191100": "Chat",
    "ba097c3a-31cf-48a7-a196-84fad50efe8d": "Landing page",
    "d08186b2-b670-4fdf-9596-7654017f9255": "Incoming call / email"
}

STATUS_MAPPING = {
    "0198bb53-c5da-41a7-98ad-c92a61706867": "Marketing qualified lead",
    "0a0808c5-5415-41f0-bea3-118cc3089959": "Regular Customer/Nurturing",
    "0da67f47-a96c-4a9c-b4f2-c2be6ca67052": "Unreachable",
    "128c3718-771a-4d1e-9035-6fa135ca5f70": "Bad lead",
    "14cfc644-e3ed-497e-8279-ed4319bb8093": "Contacted",
    "1a378dc8-ac0a-494b-9762-9a7186f15c7e": "Qualification",
    "1cc41f20-8add-4491-a3ad-78e5881cbccd": "Enroll",
    "2cb92f28-8e87-4ea4-8263-fa2542db459e": "Temporary out - Financial Aid",
    "335c9be7-2274-4e82-9f0a-7b0fbbe9f4d9": "Temporary Out - Application",
    "360f05e5-9ca2-4fac-a672-de061abb1314": "Waiting for Fee Payment",
    "37a86c0e-4755-4609-baca-fe92ce33577a": "Closed lost",
    "51adc3ec-3503-4b10-a00b-8be3b0e11f08": "Do not contact",
    "718f89ed-53bb-4d1c-9d79-7cc9fbf3ed6": "Confirmed enrollment",
    "7a90900b-53b5-4598-92b3-0aee90626c56": "Application",
    "80d24fdc-2ff2-473f-b5fa-66e208314a38": "Temporary Out - First Outreach",
    "861b1c69-45ce-4cf3-84a4-0a2ef5ed1fae": "Application Process",
    "92154e4b-f095-43fb-91ce-070fb0985c41": "Sales qualified lead",
    "acbf4071-aba9-4d7e-aba0-32a8af60e2e8": "Temporary Out - Interview",
    "c2b4f607-23ed-403b-8b44-ac096d723756": "Waiting for FA results",
    "c9e35b93-4ea3-40cd-babe-dbc1db81d8b6": "Returning Lead",
    "ceb70b3c-985f-4867-ae7c-88f9dd710688": "Interview",
    "cebaddbf-a15f-4b51-b432-84cf95fdb2bf": "Nurturing",
    "d5863a77-8433-4b97-906e-f6bf18c2a391": "Temporary Out - Contacted",
    "d790a45d-03ff-4ddb-9dea-8087722c582c": "First Outreach",
    "ddcb3f67-6f05-4100-900e-e6dd88d5bcf5": "Academically not qualified",
    "e2b8807c-6aca-4a9d-ab4a-1d8fc16a9767": "Cancel the enrollment",
    "f2310bc5-419b-4e46-b313-c8c1d87ebd0f": "Reschedule the enrollment",
    "f49341e6-b2aa-49a0-90f1-d5d149be8325": "Enrolled/Confirm",
    "fb2df0a2-fb55-4fcc-8e46-a8da02c449c8": "Converted"
}

# ==============================
# 🪙 STEP 1: Get Access Token
# ==============================
def get_access_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to get token: {response.status_code} - {response.text}")

    token_json = response.json()
    return token_json.get("access_token")

# ==============================
# 📡 STEP 2: Fetch Leads by RegisterMethod
# ==============================
def fetch_leads_by_register_method(token):
    filter_query = f"$filter=RegisterMethod/Id eq {REGISTER_METHOD_GUID}"
    url = f"{ODATA_URL}?{filter_query}"

    headers = {
        "Authorization": f"Bearer {token}",
        "ForceUseSession": "true",
        "BPMCSRF": ""
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch leads: {response.status_code} - {response.text}")

    return response.json()

# ==============================
# 📡 STEP 2-1: Fetch Leads by Date
# ==============================

def fetch_leads_by_date(token, start_date="2025-10-07T00:00:00Z"):
    """
    Fetch leads created on or after the given start_date.
    start_date must be in ISO 8601 format (UTC): YYYY-MM-DDTHH:mm:ssZ
    """
    filter_query = f"$filter=CreatedOn ge {start_date}"
    url = f"{ODATA_URL}?{filter_query}"

    headers = {
        "Authorization": f"Bearer {token}",
        "ForceUseSession": "true",
        "BPMCSRF": ""
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch leads: {response.status_code} - {response.text}")

    return response.json()

# ==============================
# 📊 STEP 3: Parse and Create DataFrame
# ==============================
def create_dataframe(leads_data):
    """
    Extract relevant fields from leads and create a pandas DataFrame
    """
    leads_list = leads_data.get("value", [])
    
    if not leads_list:
        print("⚠️ No leads found")
        return pd.DataFrame()
    
    # Extract relevant fields for each lead
    parsed_leads = []
    for lead in leads_list:
        # Get GUID values
        language_id = lead.get("UsrLanguageLookupId", "")
        location_id = lead.get("UsrDesiredLocatLookup2Id", "")
        register_method_id = lead.get("RegisterMethodId", "")
        status_id = lead.get("QualifyStatusId", "")
        
        parsed_lead = {
            # Basic Contact Info
            "First_Name": lead.get("UsrFirstNameString", ""),
            "Last_Name": lead.get("UsrLastNameString", ""),
            "Email": lead.get("Email", ""),
            "Mobile_Phone": lead.get("MobilePhone", ""),
            
            # Course & Outreach Info
            "Course_Of_Interest": lead.get("UsrCourseOfInterestFromInitialOutreach", ""),
            "Language": LANGUAGE_MAPPING.get(language_id, language_id),  # Map to readable name
            #"Language_ID": language_id,
            "Best_Way_To_Reach": lead.get("UsrBestWayToReach", ""),
            "Desired_Location": LOCATION_MAPPING.get(location_id, location_id),  # Map to readable name
            #"Desired_Location_ID": location_id,
            
            # External & Metadata
            "External_ID": lead.get("UsrIDExternal", ""),
            #"Chat_Summary": lead.get("UsrChatSummary", ""),
            "External_Metadata": lead.get("UsrExternalMetadata", ""),
            "Form_Source": lead.get("UsrFormSource", ""),
            #"Transcript": lead.get("UsrTranscript", ""),
            "Register_Method": REGISTER_METHOD_MAPPING.get(register_method_id, register_method_id),  # Map to readable name
            "Register_Method_ID": register_method_id,
            
            # Lead Status
            "Status": STATUS_MAPPING.get(status_id, status_id),  # Map to readable name
           # "Status_ID": status_id,
            
            "Created_On": lead.get("CreatedOn", ""),
            "Modified_On": lead.get("ModifiedOn", ""),
            
        }
        parsed_leads.append(parsed_lead)
    
    df = pd.DataFrame(parsed_leads)
    return df

# ==============================
# 🧾 MAIN
# ==============================
if __name__ == "__main__":
    try:
        print("🔐 Getting access token...")
        token = get_access_token()
        print("✅ Token received.")

        print("📡 Fetching leads...")
        result = fetch_leads_by_date(token)
        print("✅ Leads fetched successfully.\n")

        print("📊 Creating DataFrame...")
        df = create_dataframe(result)
        
        if not df.empty:
            print(f"✅ DataFrame created with {len(df)} leads\n")
            
            # Display basic info
            print("=" * 100)
            print("LEADS SUMMARY")
            print("=" * 100)
            
            # Set pandas display options for better viewing
            pd.set_option('display.max_columns', None)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 50)
            
            print(df.to_string(index=False))
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"leads_export.csv"
            df.to_csv(csv_filename, index=False)
            print(f"\n💾 Data saved to: {csv_filename}")
            
            # Print summary statistics
            print(f"\n📈 STATISTICS:")
            print(f"   Total Leads: {len(df)}")
            print(f"   With Email: {df['Email'].notna().sum()}")
            print(f"   With Phone: {df['Mobile_Phone'].notna().sum()}")
            
            # Language breakdown
            if 'Language' in df.columns:
                print(f"\n   Language Breakdown:")
                lang_counts = df['Language'].value_counts()
                for lang, count in lang_counts.items():
                    print(f"      {lang}: {count}")
            
            # Location breakdown
            if 'Desired_Location' in df.columns:
                print(f"\n   Location Preferences:")
                loc_counts = df['Desired_Location'].value_counts()
                for loc, count in loc_counts.items():
                    print(f"      {loc}: {count}")
            
            # Registration method breakdown
            if 'Register_Method' in df.columns:
                print(f"\n   Registration Methods:")
                reg_counts = df['Register_Method'].value_counts()
                for method, count in reg_counts.items():
                    print(f"      {method}: {count}")
            
            # Status breakdown
            if 'Status' in df.columns:
                print(f"\n   Lead Status:")
                status_counts = df['Status'].value_counts()
                for status, count in status_counts.items():
                    print(f"      {status}: {count}")
        
    except Exception as e:
        print(f"⚠️ Error: {e}")

