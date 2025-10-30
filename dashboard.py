import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import requests
import json
import io
import base64

# ==============================
# 🔐 CONFIGURATION
# ==============================
TOKEN_URL = "https://christinevalmy-is.creatio.com/connect/token"
ODATA_URL = "https://christinevalmy.creatio.com/0/odata/Lead"

# Use Streamlit secrets for production, fallback to hardcoded values for local dev
try:
    CLIENT_ID = st.secrets["CREATIO_CLIENT_ID"]
    CLIENT_SECRET = st.secrets["CREATIO_CLIENT_SECRET"]
except:
    CLIENT_ID = "4D8E6F5A8AC8F7BB66EA1A3DC60AE5BC"
    CLIENT_SECRET = "86F4E90DA7949169E5E81E3D743E49F08B088BBD5E76709EAAB17FBE42814201"

REGISTER_METHOD_GUID = "7928af33-a08e-443f-b949-4ba4ab251617"

# Mappings
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
# 🔄 DATA FETCHING FUNCTIONS
# ==============================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_access_token():
    """Get access token from Creatio"""
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to get token: {response.status_code} - {response.text}")
        return None
    
    return response.json().get("access_token")

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_leads_data():
    """Fetch leads data from Creatio API"""
    token = get_access_token()
    if not token:
        return None
    start_date="2025-10-07T00:00:00Z"
    filter_query = f"$filter=CreatedOn ge {start_date}"
    #filter_query = f"$filter=RegisterMethod/Id eq {REGISTER_METHOD_GUID}"
    url = f"{ODATA_URL}?{filter_query}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "ForceUseSession": "true",
        "BPMCSRF": ""
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        st.error(f"Failed to fetch leads: {response.status_code} - {response.text}")
        return None
    
    return response.json()

def process_leads_data(leads_data):
    """Process leads data into DataFrame"""
    leads_list = leads_data.get("value", [])
    
    if not leads_list:
        return pd.DataFrame()
    
    parsed_leads = []
    for lead in leads_list:
        language_id = lead.get("UsrLanguageLookupId", "")
        location_id = lead.get("UsrDesiredLocatLookup2Id", "")
        register_method_id = lead.get("RegisterMethodId", "")
        status_id = lead.get("QualifyStatusId", "")
        
        parsed_lead = {
            "First_Name": lead.get("UsrFirstNameString", ""),
            "Last_Name": lead.get("UsrLastNameString", ""),
            "Email": lead.get("Email", ""),
            "Mobile_Phone": lead.get("MobilePhone", ""),
            "Course_Of_Interest": lead.get("UsrCourseOfInterestFromInitialOutreach", ""),
            "Language": LANGUAGE_MAPPING.get(language_id, language_id),
            "Best_Way_To_Reach": lead.get("UsrBestWayToReach", ""),
            "Desired_Location": LOCATION_MAPPING.get(location_id, location_id),
            "External_ID": lead.get("UsrIDExternal", ""),
            "External_Metadata": lead.get("UsrExternalMetadata", ""),
            "Form_Source": lead.get("UsrFormSource", ""),
            "Register_Method": REGISTER_METHOD_MAPPING.get(register_method_id, register_method_id),
            "Status": STATUS_MAPPING.get(status_id, status_id),
            "Created_On": lead.get("CreatedOn", ""),
            "Modified_On": lead.get("ModifiedOn", ""),
        }
        parsed_leads.append(parsed_lead)
    
    return pd.DataFrame(parsed_leads)

# ==============================
# 📊 VISUALIZATION FUNCTIONS
# ==============================
def create_registration_method_chart(df):
    """Create registration method distribution chart"""
    reg_counts = df['Register_Method'].value_counts()
    
    fig = px.pie(values=reg_counts.values, names=reg_counts.index, 
                  title="Lead Registration Methods Distribution")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_status_distribution_chart(df):
    """Create status distribution chart"""
    status_counts = df['Status'].value_counts()
    
    fig = px.bar(x=status_counts.index, y=status_counts.values,
                 title="Lead Status Distribution",
                 labels={'x': 'Status', 'y': 'Number of Leads'})
    fig.update_xaxes(tickangle=45)
    return fig

def create_sentryskin_analysis(df):
    """Create SentrySkin form source analysis"""
    sentryskin_df = df[df['Register_Method'] == 'sentryskin']
    
    if len(sentryskin_df) == 0:
        return None
    
    form_sources = sentryskin_df['Form_Source'].value_counts()
    
    fig = px.pie(values=form_sources.values, names=form_sources.index,
                  title="SentrySkin Form Sources Distribution")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_status_heatmap(df):
    """Create status vs registration method heatmap"""
    crosstab = pd.crosstab(df['Register_Method'], df['Status'])
    
    fig = px.imshow(crosstab.values, 
                    labels=dict(x="Status", y="Registration Method", color="Count"),
                    x=crosstab.columns,
                    y=crosstab.index,
                    title="Lead Status by Registration Method",
                    color_continuous_scale="Reds")
    fig.update_xaxes(tickangle=45)
    return fig

def create_sankey_diagram(df, selected_methods=None, selected_sources=None, selected_statuses=None):
    """Create enhanced Sankey diagram with filtering and better colors"""
    
    # Filter data based on selections
    filtered_df = df.copy()
    
    if selected_methods:
        filtered_df = filtered_df[filtered_df['Register_Method'].isin(selected_methods)]
    if selected_sources:
        filtered_df = filtered_df[filtered_df['Form_Source'].isin(selected_sources)]
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['Status'].isin(selected_statuses)]
    
    if filtered_df.empty:
        return None
    
    # Prepare data for Sankey
    reg_methods = filtered_df['Register_Method'].unique()
    form_sources = filtered_df['Form_Source'].unique()
    statuses = filtered_df['Status'].unique()
    
    # Create node mapping with better organization
    all_nodes = list(reg_methods) + list(form_sources) + list(statuses)
    node_mapping = {node: i for i, node in enumerate(all_nodes)}
    
    # Define distinct color schemes for better visualization
    method_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    source_colors = ['#FF4757', '#2ED573', '#1E90FF', '#FFA502', '#FF6348', '#9C88FF', '#FF6B9D']
    status_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD', '#00D2D3', '#FF9F43', '#FF4757', '#2ED573', '#1E90FF', '#FFA502', '#FF6348']
    
    # Create node colors with distinct colors for each category
    node_colors = []
    for node in all_nodes:
        if node in reg_methods:
            # Each registration method gets a unique color
            node_colors.append(method_colors[list(reg_methods).index(node) % len(method_colors)])
        elif node in form_sources:
            # Each form source gets a unique color
            node_colors.append(source_colors[list(form_sources).index(node) % len(source_colors)])
        else:
            # Each status gets a unique color
            node_colors.append(status_colors[list(statuses).index(node) % len(status_colors)])
    
    # Count flows
    source_nodes = []
    target_nodes = []
    values = []
    labels = []
    link_colors = []
    
    # Registration Method -> Form Source
    for method in reg_methods:
        method_df = filtered_df[filtered_df['Register_Method'] == method]
        for source in form_sources:
            count = len(method_df[method_df['Form_Source'] == source])
            if count > 0:
                source_nodes.append(node_mapping[method])
                target_nodes.append(node_mapping[source])
                values.append(count)
                labels.append(f"{method} → {source} ({count})")
                # Use method color for links with better visibility
                method_color = method_colors[list(reg_methods).index(method) % len(method_colors)]
                r = int(method_color[1:3], 16)
                g = int(method_color[3:5], 16)
                b = int(method_color[5:7], 16)
                link_colors.append(f"rgba({r}, {g}, {b}, 0.7)")
    
    # Form Source -> Status
    for source in form_sources:
        source_df = filtered_df[filtered_df['Form_Source'] == source]
        for status in statuses:
            count = len(source_df[source_df['Status'] == status])
            if count > 0:
                source_nodes.append(node_mapping[source])
                target_nodes.append(node_mapping[status])
                values.append(count)
                labels.append(f"{source} → {status} ({count})")
                # Use source color for links with better visibility
                source_color = source_colors[list(form_sources).index(source) % len(source_colors)]
                r = int(source_color[1:3], 16)
                g = int(source_color[3:5], 16)
                b = int(source_color[5:7], 16)
                link_colors.append(f"rgba({r}, {g}, {b}, 0.7)")
    
    if not source_nodes:
        return None
    
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=15,
            thickness=25,
            line=dict(color="black", width=1),
            label=[],  # Empty labels - we'll add them as annotations
            color=node_colors,
            hovertemplate='%{label}<br>Count: %{value}<extra></extra>',
            x=[0.15] * len(reg_methods) + [0.5] * len(form_sources) + [0.85] * len(statuses),
            y=[i/(len(reg_methods)-1) if len(reg_methods) > 1 else 0.5 for i in range(len(reg_methods))] + 
              [i/(len(form_sources)-1) if len(form_sources) > 1 else 0.5 for i in range(len(form_sources))] + 
              [i/(len(statuses)-1) if len(statuses) > 1 else 0.5 for i in range(len(statuses))]
        ),
        link=dict(
            source=source_nodes,
            target=target_nodes,
            value=values,
            color=link_colors,
            hovertemplate='%{source.label} → %{target.label}<br>Count: %{value}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        title=dict(
            text="Lead Flow Analysis",
            font=dict(size=16, color='black', family="Arial"),
            x=0.5,
            y=0.95
        ),
        font=dict(size=11, color='black', family="Arial"),
        height=700,
        width=1400,  # Increased width to accommodate external labels
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(l=150, r=200, t=80, b=50)  # Increased margins for external labels
    )
    
    # Add external labels for registration methods (left side)
    for i, method in enumerate(reg_methods):
        y_pos = i/(len(reg_methods)-1) if len(reg_methods) > 1 else 0.5
        fig.add_annotation(
            x=0.05, y=y_pos,
            text=f"<b>{method}</b>",
            showarrow=False,
            font=dict(size=12, color='black', family="Arial"),
            xref="paper", yref="paper",
            xanchor="right"
        )
    
    # Add external labels for form sources (center)
    for i, source in enumerate(form_sources):
        y_pos = i/(len(form_sources)-1) if len(form_sources) > 1 else 0.5
        fig.add_annotation(
            x=0.5, y=y_pos,
            text=f"<b>{source}</b>",
            showarrow=False,
            font=dict(size=12, color='black', family="Arial"),
            xref="paper", yref="paper",
            xanchor="center"
        )
    
    # Add external labels for lead statuses (right side)
    for i, status in enumerate(statuses):
        y_pos = i/(len(statuses)-1) if len(statuses) > 1 else 0.5
        fig.add_annotation(
            x=0.95, y=y_pos,
            text=f"<b>{status}</b>",
            showarrow=False,
            font=dict(size=12, color='black', family="Arial"),
            xref="paper", yref="paper",
            xanchor="left"
        )
    
    # Add simple section headers
    fig.add_annotation(
        x=0.05, y=1.02,
        text="Registration Methods",
        showarrow=False,
        font=dict(size=12, color='black', family="Arial"),
        xref="paper", yref="paper",
        xanchor="center"
    )
    
    fig.add_annotation(
        x=0.5, y=1.02,
        text="Form Sources",
        showarrow=False,
        font=dict(size=12, color='black', family="Arial"),
        xref="paper", yref="paper",
        xanchor="center"
    )
    
    fig.add_annotation(
        x=0.95, y=1.02,
        text="Lead Statuses",
        showarrow=False,
        font=dict(size=12, color='black', family="Arial"),
        xref="paper", yref="paper",
        xanchor="center"
    )
    
    return fig

def create_landing_vs_sentryskin_comparison(df):
    """Create comparison chart between Landing Page and SentrySkin lead statuses"""
    print("\n📊 Creating Landing Page vs SentrySkin Comparison...")
    
    if df.empty:
        return None
    
    # Filter for Landing Page and SentrySkin only
    comparison_df = df[df['Register_Method'].isin(['Landing page', 'sentryskin'])]
    
    if comparison_df.empty:
        return None
    
    # Get status counts for each method
    landing_statuses = comparison_df[comparison_df['Register_Method'] == 'Landing page']['Status'].value_counts()
    sentryskin_statuses = comparison_df[comparison_df['Register_Method'] == 'sentryskin']['Status'].value_counts()
    
    # Get all unique statuses
    all_statuses = set(landing_statuses.index) | set(sentryskin_statuses.index)
    
    # Create comparison data
    comparison_data = []
    for status in all_statuses:
        landing_count = landing_statuses.get(status, 0)
        sentryskin_count = sentryskin_statuses.get(status, 0)
        
        # Calculate percentages
        landing_total = len(comparison_df[comparison_df['Register_Method'] == 'Landing page'])
        sentryskin_total = len(comparison_df[comparison_df['Register_Method'] == 'sentryskin'])
        
        landing_pct = (landing_count / landing_total * 100) if landing_total > 0 else 0
        sentryskin_pct = (sentryskin_count / sentryskin_total * 100) if sentryskin_total > 0 else 0
        
        comparison_data.append({
            'Status': status,
            'Landing Page': landing_pct,
            'SentrySkin': sentryskin_pct,
            'Landing Count': landing_count,
            'SentrySkin Count': sentryskin_count
        })
    
    comparison_df_viz = pd.DataFrame(comparison_data)
    
    # Sort by the maximum percentage between Landing Page and SentrySkin (descending order)
    comparison_df_viz['Max_Percentage'] = comparison_df_viz[['Landing Page', 'SentrySkin']].max(axis=1)
    comparison_df_viz = comparison_df_viz.sort_values('Max_Percentage', ascending=False)
    
    # Create grouped bar chart
    fig = go.Figure()
    
    # Add Landing Page bars
    fig.add_trace(go.Bar(
        name='Landing Page',
        x=comparison_df_viz['Status'],
        y=comparison_df_viz['Landing Page'],
        marker_color='#FF6B6B',
        text=[f"{count}<br>({pct:.1f}%)" for count, pct in zip(comparison_df_viz['Landing Count'], comparison_df_viz['Landing Page'])],
        textposition='outside',
        hovertemplate='<b>Landing Page</b><br>Status: %{x}<br>Count: %{customdata[0]}<br>Percentage: %{y:.1f}%<extra></extra>',
        customdata=list(zip(comparison_df_viz['Landing Count'], comparison_df_viz['Landing Page']))
    ))
    
    # Add SentrySkin bars
    fig.add_trace(go.Bar(
        name='SentrySkin',
        x=comparison_df_viz['Status'],
        y=comparison_df_viz['SentrySkin'],
        marker_color='#4ECDC4',
        text=[f"{count}<br>({pct:.1f}%)" for count, pct in zip(comparison_df_viz['SentrySkin Count'], comparison_df_viz['SentrySkin'])],
        textposition='outside',
        hovertemplate='<b>SentrySkin</b><br>Status: %{x}<br>Count: %{customdata[0]}<br>Percentage: %{y:.1f}%<extra></extra>',
        customdata=list(zip(comparison_df_viz['SentrySkin Count'], comparison_df_viz['SentrySkin']))
    ))
    
    fig.update_layout(
        title="Lead Status Distribution: Landing Page vs SentrySkin",
        xaxis_title="Lead Status",
        yaxis_title="Percentage (%)",
        barmode='group',
        height=600,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Rotate x-axis labels for better readability
    fig.update_xaxes(tickangle=45)
    
    return fig

def fetch_sentryskin_data_from_api():
    """Fetch SentrySkin data directly from n8n API"""
    try:
        # Import the fetch function from the existing script
        import subprocess
        import sys
        
        # Run the fetch script to get fresh data
        result = subprocess.run([sys.executable, "fetch_sentryskin_data.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            st.error(f"Error fetching SentrySkin data: {result.stderr}")
            return None
            
        # Run the extraction script
        result = subprocess.run([sys.executable, "extract_sentryskin_fields.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            st.error(f"Error extracting SentrySkin fields: {result.stderr}")
            return None
            
        # Run the user analysis script
        result = subprocess.run([sys.executable, "analyze_sentryskin_users.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            st.error(f"Error analyzing SentrySkin users: {result.stderr}")
            return None
            
        # Run the post-Oct 7th analysis script
        result = subprocess.run([sys.executable, "analyze_post_oct7_2025.py"], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            st.error(f"Error generating post-Oct 7th analysis: {result.stderr}")
            return None
            
        # Now load the generated data
        try:
            df = pd.read_csv("sentryskin_post_oct7_2025_detailed_report.csv")
            return df
        except FileNotFoundError:
            st.error("Analysis completed but report file not found")
            return None
            
    except subprocess.TimeoutExpired:
        st.error("Data fetching timed out. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error in data pipeline: {str(e)}")
        return None

def load_sentryskin_user_analysis():
    """Load SentrySkin user analysis data - try API first, fallback to static file"""
    # First try to fetch fresh data from API
    df = fetch_sentryskin_data_from_api()
    
    if df is not None and not df.empty:
        return df
    
    # Fallback to static file if API fails
    try:
        df = pd.read_csv("sentryskin_post_oct7_2025_detailed_report.csv")
        return df
    except FileNotFoundError:
        return None

def create_device_distribution_chart(df):
    """Create device distribution chart for SentrySkin users"""
    if df is None or df.empty:
        return None
    
    # Count devices
    device_counts = {}
    for devices in df['devices']:
        if pd.notna(devices):
            for device in devices.split(', '):
                device = device.strip()
                device_counts[device] = device_counts.get(device, 0) + 1
    
    if not device_counts:
        return None
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(device_counts.keys()),
        values=list(device_counts.values()),
        hole=0.3,
        textinfo='label+percent',
        textfont_size=12
    )])
    
    fig.update_layout(
        title="User Analysis - Device Distribution",
        font=dict(size=14, color='black', family="Arial"),
        height=400,
        showlegend=True
    )
    
    return fig

def create_browser_distribution_chart(df):
    """Create browser distribution chart for SentrySkin users"""
    if df is None or df.empty:
        return None
    
    # Count browsers
    browser_counts = {}
    for browsers in df['browsers']:
        if pd.notna(browsers):
            for browser in browsers.split(', '):
                browser = browser.strip()
                browser_counts[browser] = browser_counts.get(browser, 0) + 1
    
    if not browser_counts:
        return None
    
    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=list(browser_counts.keys()),
        y=list(browser_counts.values()),
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
        text=list(browser_counts.values()),
        textposition='outside'
    )])
    
    fig.update_layout(
        title="User Analysis - Browser Distribution",
        xaxis_title="Browser",
        yaxis_title="Number of Users",
        font=dict(size=14, color='black', family="Arial"),
        height=400,
        margin=dict(l=50, r=50, t=80, b=80),
        xaxis=dict(tickangle=0),
        yaxis=dict(range=[0, max(browser_counts.values()) * 1.2])
    )
    
    return fig

def create_os_distribution_chart(df):
    """Create OS distribution chart for SentrySkin users"""
    if df is None or df.empty:
        return None
    
    # Count operating systems
    os_counts = {}
    for os_list in df['operating_systems']:
        if pd.notna(os_list):
            for os in os_list.split(', '):
                os = os.strip()
                os_counts[os] = os_counts.get(os, 0) + 1
    
    if not os_counts:
        return None
    
    # Create horizontal bar chart
    fig = go.Figure(data=[go.Bar(
        y=list(os_counts.keys()),
        x=list(os_counts.values()),
        orientation='h',
        marker_color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
        text=list(os_counts.values()),
        textposition='outside'
    )])
    
    fig.update_layout(
        title="User Analysis - OS Distribution",
        xaxis_title="Number of Users",
        yaxis_title="Operating System",
        font=dict(size=14, color='black', family="Arial"),
        height=400
    )
    
    return fig

def create_conversation_distribution_chart(df):
    """Create conversation count distribution chart"""
    if df is None or df.empty:
        return None
    
    # Create histogram
    fig = go.Figure(data=[go.Histogram(
        x=df['conversation_count'],
        nbinsx=20,
        marker_color='#4ECDC4',
        opacity=0.7
    )])
    
    fig.update_layout(
        title="User Analysis - Conversation Count Distribution",
        xaxis_title="Number of Conversations",
        yaxis_title="Number of Users",
        font=dict(size=14, color='black', family="Arial"),
        height=400
    )
    
    return fig

# ==============================
# 🎨 DASHBOARD LAYOUT
# ==============================
def main():
    st.set_page_config(
        page_title="Creatio Lead Analysis Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("📊 Creatio Lead Analysis Dashboard")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("🔄 Data Controls")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Last Updated:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # Data loading
    with st.spinner("🔄 Fetching latest data from Creatio..."):
        leads_data = fetch_leads_data()
    
    if leads_data is None:
        st.error("❌ Failed to fetch data. Please check your connection and try again.")
        return
    
    df = process_leads_data(leads_data)
    
    if df.empty:
        st.warning("⚠️ No leads found in the data.")
        return
    
    # Key metrics
    st.subheader("📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Leads", len(df))
    
    with col2:
        sentryskin_count = len(df[df['Register_Method'] == 'sentryskin'])
        st.metric("SentrySkin Leads", sentryskin_count)
    
    with col3:
        landing_page_count = len(df[df['Register_Method'] == 'Landing page'])
        st.metric("Landing Page Leads", landing_page_count)
    
    with col4:
        enrolled_count = len(df[df['Status'] == 'Enrolled/Confirm'])
        st.metric("Enrolled Leads", enrolled_count)
    
    st.markdown("---")
    
    # Charts section
    st.subheader("📊 Lead Analysis Charts")
    
    # Define filters first
    all_methods = df['Register_Method'].unique()
    all_sources = df['Form_Source'].unique()
    all_statuses = df['Status'].unique()
    
    # Apply filters to all charts
    filtered_df = df.copy()
    
    # Row 1: Registration Methods and Status Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_registration_method_chart(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_status_distribution_chart(filtered_df), use_container_width=True)
    
    # Row 2: SentrySkin Analysis and Heatmap
    col1, col2 = st.columns(2)
    
    with col1:
        sentryskin_chart = create_sentryskin_analysis(filtered_df)
        if sentryskin_chart:
            st.plotly_chart(sentryskin_chart, use_container_width=True)
        else:
            st.info("No SentrySkin leads found")
    
    with col2:
        st.plotly_chart(create_status_heatmap(filtered_df), use_container_width=True)
    
    # Row 3: Landing Page vs SentrySkin Comparison
    st.subheader("🎯 Landing Page vs SentrySkin Value Analysis")
    
    comparison_chart = create_landing_vs_sentryskin_comparison(filtered_df)
    if comparison_chart:
        st.plotly_chart(comparison_chart, use_container_width=True)
    else:
        st.warning("⚠️ No Landing Page or SentrySkin leads found for comparison")
    
    # Row 4: User Analysis
    st.subheader("👥 User Analysis")
    
    # SentrySkin data refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("**Real-time SentrySkin user analysis**")
    with col2:
        if st.button("🔄 Refresh SentrySkin Data", help="Fetch fresh data from n8n API"):
            with st.spinner("🔄 Fetching fresh SentrySkin data from n8n API..."):
                # Clear any cached data and fetch fresh
                sentryskin_users_df = fetch_sentryskin_data_from_api()
                if sentryskin_users_df is not None:
                    st.success("✅ SentrySkin data refreshed successfully!")
                else:
                    st.error("❌ Failed to refresh SentrySkin data")
            st.rerun()
    
    # Load SentrySkin user analysis data
    with st.spinner("🔄 Loading SentrySkin user analysis..."):
        sentryskin_users_df = load_sentryskin_user_analysis()
    
    if sentryskin_users_df is not None and not sentryskin_users_df.empty:
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Active Users",
                value=len(sentryskin_users_df),
                help="Users with interactions after October 7th, 2025"
            )
        
        with col2:
            total_conversations = sentryskin_users_df['conversation_count'].sum()
            st.metric(
                label="Total Conversations",
                value=total_conversations,
                help="Total conversations from active users"
            )
        
        with col3:
            avg_conversations = sentryskin_users_df['conversation_count'].mean()
            st.metric(
                label="Avg Conversations/User",
                value=round(avg_conversations),
                help="Average conversations per active user"
            )
        
        with col4:
            max_conversations = sentryskin_users_df['conversation_count'].max()
            st.metric(
                label="Max Conversations",
                value=max_conversations,
                help="Highest number of conversations by a single user"
            )
        
        # Create charts in two rows
        # Row 1: Device and Browser Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            device_chart = create_device_distribution_chart(sentryskin_users_df)
            if device_chart:
                st.plotly_chart(device_chart, use_container_width=True)
            else:
                st.info("No device data available")
        
        with col2:
            browser_chart = create_browser_distribution_chart(sentryskin_users_df)
            if browser_chart:
                st.plotly_chart(browser_chart, use_container_width=True)
            else:
                st.info("No browser data available")
        
        # Row 2: OS Distribution and Conversation Count
        col1, col2 = st.columns(2)
        
        with col1:
            os_chart = create_os_distribution_chart(sentryskin_users_df)
            if os_chart:
                st.plotly_chart(os_chart, use_container_width=True)
            else:
                st.info("No OS data available")
        
        with col2:
            conversation_chart = create_conversation_distribution_chart(sentryskin_users_df)
            if conversation_chart:
                st.plotly_chart(conversation_chart, use_container_width=True)
            else:
                st.info("No conversation data available")
        
        # Top Active Users Table
        st.subheader("🏆 Top 10 Most Active Users")
        
        # Sort by conversation count and show top 10
        top_users = sentryskin_users_df.nlargest(10, 'conversation_count')[
            ['user_id', 'conversation_count', 'first_interaction', 'last_interaction', 'devices', 'browsers', 'operating_systems']
        ]
        
        # Format timestamps for display
        top_users_display = top_users.copy()
        top_users_display['first_interaction'] = pd.to_datetime(top_users_display['first_interaction']).dt.strftime('%Y-%m-%d %H:%M')
        top_users_display['last_interaction'] = pd.to_datetime(top_users_display['last_interaction']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Rename columns for better display
        top_users_display.columns = ['User ID', 'Conversations', 'First Interaction', 'Last Interaction', 'Devices', 'Browsers', 'OS']
        
        st.dataframe(top_users_display, use_container_width=True)
        
        # Download button for user analysis data
        csv_data = sentryskin_users_df.to_csv(index=False)
        st.download_button(
            label="📥 Download User Analysis Data",
            data=csv_data,
            file_name=f"sentryskin_user_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
    else:
        st.warning("⚠️ SentrySkin user analysis data not found.")
        st.info("💡 **To get fresh data:** Click the '🔄 Refresh SentrySkin Data' button above to fetch data directly from the n8n API.")
        st.markdown("""
        **Data Pipeline:**
        1. 🔄 Fetch raw data from n8n API
        2. 📊 Extract user fields and device info  
        3. 📈 Analyze user patterns and conversations
        4. 📋 Generate post-October 7th report
        """)
    
    # Add filters for all charts
    with st.expander("🔧 Chart Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_methods = st.multiselect(
                "Filter Registration Methods",
                all_methods,
                default=all_methods,
                key="chart_methods",
                help="Select which registration methods to show"
            )
        
        with col2:
            selected_sources = st.multiselect(
                "Filter Form Sources",
                all_sources,
                default=all_sources,
                key="chart_sources",
                help="Select which form sources to show"
            )
        
        with col3:
            selected_statuses = st.multiselect(
                "Filter Statuses",
                all_statuses,
                default=all_statuses[:10] if len(all_statuses) > 10 else all_statuses,
                key="chart_statuses",
                help="Select which statuses to show"
            )
    
    # Apply filters to all charts after getting filter values
    if selected_methods:
        filtered_df = filtered_df[filtered_df['Register_Method'].isin(selected_methods)]
    if selected_sources:
        filtered_df = filtered_df[filtered_df['Form_Source'].isin(selected_sources)]
    if selected_statuses:
        filtered_df = filtered_df[filtered_df['Status'].isin(selected_statuses)]
    
    st.info(f"📊 Showing {len(filtered_df)} leads with current filters")
    
    # Detailed statistics (using filtered data) in three columns
    st.subheader("📋 Detailed Statistics")
    
    if len(filtered_df) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Registration Methods:**")
            reg_counts = filtered_df['Register_Method'].value_counts()
            for method, count in reg_counts.items():
                percentage = (count / len(filtered_df)) * 100
                st.write(f"• {method}: {count} leads ({percentage:.1f}%)")
        
        with col2:
            # SentrySkin breakdown
            sentryskin_df = filtered_df[filtered_df['Register_Method'] == 'sentryskin']
            if len(sentryskin_df) > 0:
                st.write("**SentrySkin Form Sources:**")
                form_sources = sentryskin_df['Form_Source'].value_counts()
                for source, count in form_sources.items():
                    percentage = (count / len(sentryskin_df)) * 100
                    st.write(f"• {source}: {count} leads ({percentage:.1f}%)")
            else:
                st.write("**Form Sources:**")
                source_counts = filtered_df['Form_Source'].value_counts()
                for source, count in source_counts.items():
                    percentage = (count / len(filtered_df)) * 100
                    st.write(f"• {source}: {count} leads ({percentage:.1f}%)")
        
        with col3:
            st.write("**Top Lead Statuses:**")
            status_counts = filtered_df['Status'].value_counts().head(10)
            for status, count in status_counts.items():
                percentage = (count / len(filtered_df)) * 100
                st.write(f"• {status}: {count} leads ({percentage:.1f}%)")
        
        # Data table
        st.subheader("📋 Filtered Data")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered CSV",
            data=csv,
            file_name=f"filtered_leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No data available with current filters")

if __name__ == "__main__":
    main()
