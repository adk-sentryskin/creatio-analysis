# Creatio Lead Analysis Dashboard Configuration
# =============================================

# Dashboard Settings
DASHBOARD_PORT=8501
DASHBOARD_HOST=0.0.0.0

# Data Fetching Settings
CREATIO_BASE_URL="https://christinevalmy.creatio.com"
SENTRYSKIN_BASE_URL="https://sentryskin.app.n8n.cloud/api/v1/executions"
SENTRYSKIN_WORKFLOW_ID="V7n2R2x0bj99pQhK"

# Analysis Settings
ANALYSIS_START_DATE="2024-10-07"
POST_OCT7_DATE="2025-10-07"

# File Paths
LEADS_EXPORT_FILE="leads_export.csv"
SENTRYSKIN_RAW_FILE="sentryskin_user_agents.csv"
SENTRYSKIN_EXTRACTED_FILE="sentryskin_extracted_fields.csv"
USER_ANALYSIS_FILE="sentryskin_user_device_analysis.csv"
POST_OCT7_REPORT_FILE="sentryskin_post_oct7_2025_detailed_report.csv"

# Dashboard Features
ENABLE_REFRESH_BUTTON=true
ENABLE_DATA_DOWNLOAD=true
ENABLE_FILTERS=true
SHOW_USER_ANALYSIS=true

# Logging
LOG_LEVEL="INFO"
LOG_FILE="dashboard.log"

# Performance
CACHE_TIMEOUT=3600  # 1 hour in seconds
MAX_FILE_SIZE_MB=100
