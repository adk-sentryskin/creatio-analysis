# Creatio Lead Analysis Dashboard

A comprehensive automated pipeline for analyzing Creatio leads and SentrySkin user interactions with an interactive Streamlit dashboard.

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)
```bash
# Make deployment script executable
chmod +x deploy.sh

# Run full automated pipeline
./deploy.sh

# Or run dashboard only (skip data processing)
./deploy.sh --dashboard-only

# Or run on custom port
./deploy.sh --port 8502
```

### Option 2: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated pipeline
python automate_pipeline.py

# Or run individual scripts
python fetch_leads.py
python fetch_sentryskin_data.py
python extract_sentryskin_fields.py
python analyze_sentryskin_users.py
python analyze_post_oct7_2025.py

# Launch dashboard
streamlit run dashboard.py --server.port 8501
```

## 📁 Project Structure

```
creatio_analysis/
├── dashboard.py                    # Main Streamlit dashboard
├── automate_pipeline.py            # Automated pipeline script
├── deploy.sh                      # Deployment script
├── run_dashboard.py               # Dashboard launcher
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
│
├── fetch_leads.py                 # Fetch Creatio leads data
├── fetch_sentryskin_data.py       # Fetch SentrySkin n8n data
├── extract_sentryskin_fields.py   # Extract fields from raw data
├── analyze_sentryskin_users.py    # Analyze user device patterns
├── analyze_post_oct7_2025.py      # Generate post-Oct 7th analysis
│
├── leads_export.csv               # Creatio leads data
├── sentryskin_user_agents.csv     # Raw SentrySkin data
├── sentryskin_extracted_fields.csv # Processed SentrySkin fields
├── sentryskin_user_device_analysis.csv # User analysis results
├── sentryskin_post_oct7_2025_detailed_report.csv # Post-Oct 7th report
└── venv/                          # Virtual environment
```

## 🔧 Configuration

Edit `config.py` to customize:
- Dashboard port and host
- API endpoints and credentials
- Analysis date ranges
- File paths
- Feature toggles

## 📊 Dashboard Features

### Lead Analysis
- **Registration Methods**: Pie chart showing lead sources
- **Status Distribution**: Bar chart of lead statuses
- **SentrySkin Analysis**: Form source breakdown
- **Status Heatmap**: Registration method vs status matrix
- **Landing Page vs SentrySkin**: Value comparison analysis

### User Analysis
- **Device Distribution**: Mobile vs Desktop usage
- **Browser Distribution**: Chrome, Safari, Firefox, etc.
- **OS Distribution**: macOS, Windows, Android, etc.
- **Conversation Patterns**: Histogram of conversation counts
- **Top Active Users**: Table of most engaged users

### Interactive Features
- **Real-time Refresh**: Update data with one click
- **Interactive Filters**: Filter charts by registration method, form source, status
- **Data Download**: Export filtered data as CSV
- **Responsive Design**: Works on desktop and mobile

## 🔄 Automated Pipeline

The `automate_pipeline.py` script handles the complete data flow:

1. **Fetch Creatio Leads** - Get latest lead data from Creatio API
2. **Fetch SentrySkin Data** - Get execution data from n8n API
3. **Extract Fields** - Process raw n8n data into structured format
4. **Analyze Users** - Generate device/browser/OS analysis
5. **Post-Oct 7th Analysis** - Create detailed report for recent users
6. **Launch Dashboard** - Start interactive Streamlit app

### Pipeline Options

```bash
# Full pipeline (default)
python automate_pipeline.py

# Skip data fetching (use existing data)
python automate_pipeline.py --skip-fetch

# Skip analysis (use existing analysis)
python automate_pipeline.py --skip-analysis

# Dashboard only (skip all processing)
python automate_pipeline.py --dashboard-only

# Custom port
python automate_pipeline.py --port 8502
```

## 🌐 Deployment

### Local Development
```bash
./deploy.sh
# Dashboard available at http://localhost:8501
```

### Production Deployment
```bash
# Skip setup if environment already configured
./deploy.sh --skip-setup

# Run on custom port
./deploy.sh --port 8080
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x deploy.sh

EXPOSE 8501
CMD ["./deploy.sh", "--skip-setup", "--dashboard-only"]
```

## 📈 Data Sources

### Creatio API
- **Endpoint**: `https://christinevalmy.creatio.com`
- **Data**: Lead information, registration methods, statuses
- **Authentication**: OAuth client credentials

### SentrySkin n8n API
- **Endpoint**: `https://sentryskin.app.n8n.cloud/api/v1/executions`
- **Data**: User interactions, device info, conversation patterns
- **Authentication**: API key

## 🔍 Analysis Insights

### Key Metrics
- **Total Leads**: All leads from Creatio
- **SentrySkin Leads**: Leads from SentrySkin integration
- **Active Users**: Users with post-Oct 7th interactions
- **Device Distribution**: Mobile vs Desktop usage patterns
- **Browser Preferences**: Safari vs Chrome dominance

### Value Analysis
- **Landing Page vs SentrySkin**: Conversion rate comparison
- **Form Source Impact**: Chat vs Static-form effectiveness
- **User Engagement**: Conversation patterns and frequency

## 🛠️ Troubleshooting

### Common Issues

1. **Missing API Credentials**
   ```bash
   # Check if API keys are set in scripts
   grep -r "API_KEY" *.py
   ```

2. **Virtual Environment Issues**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   # Use different port
   ./deploy.sh --port 8502
   ```

4. **Missing Data Files**
   ```bash
   # Run full pipeline to generate missing files
   python automate_pipeline.py
   ```

### Logs and Debugging
- Check terminal output for error messages
- Dashboard logs appear in the terminal
- Data processing logs show progress and errors

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review terminal output for error messages
3. Ensure all dependencies are installed
4. Verify API credentials are correct

## 🔄 Updates and Maintenance

### Refreshing Data
```bash
# Full refresh (recommended daily)
./deploy.sh

# Quick refresh (dashboard only)
./deploy.sh --dashboard-only
```

### Updating Dependencies
```bash
pip install -r requirements.txt --upgrade
```

### Backup Data
```bash
# Backup all CSV files
cp *.csv backup/
```

---

**Last Updated**: October 28, 2025  
**Version**: 1.0.0  
**Python**: 3.13+  
**Streamlit**: 1.50.0+
