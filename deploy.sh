#!/bin/bash
"""
Deployment Script for Creatio Lead Analysis Dashboard
====================================================

This script sets up the environment and prepares for deployment:
1. Creates virtual environment if it doesn't exist
2. Installs dependencies
3. Makes scripts executable
4. Sets up proper permissions
5. Runs the automated pipeline

Usage:
    ./deploy.sh [--skip-setup] [--dashboard-only] [--port 8501]
"""

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
SKIP_SETUP=false
DASHBOARD_ONLY=false
PORT=8501

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-setup)
            SKIP_SETUP=true
            shift
            ;;
        --dashboard-only)
            DASHBOARD_ONLY=true
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--skip-setup] [--dashboard-only] [--port 8501]"
            echo ""
            echo "Options:"
            echo "  --skip-setup      Skip virtual environment setup"
            echo "  --dashboard-only  Only launch dashboard (skip data processing)"
            echo "  --port PORT       Set dashboard port (default: 8501)"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option $1"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🚀 CREATIO LEAD ANALYSIS - DEPLOYMENT SCRIPT${NC}"
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🕒 Started at: $(date)${NC}"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
    echo "Please install Python 3 and try again"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"

# Setup virtual environment
if [ "$SKIP_SETUP" = false ]; then
    echo ""
    echo -e "${YELLOW}📦 Setting up virtual environment...${NC}"
    
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo -e "${GREEN}✅ Virtual environment created${NC}"
    else
        echo -e "${GREEN}✅ Virtual environment already exists${NC}"
    fi
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    echo "Upgrading pip..."
    pip install --upgrade pip
    
    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${YELLOW}⏭️  Skipping virtual environment setup${NC}"
    # Still need to activate venv if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
fi

# Make scripts executable
echo ""
echo -e "${YELLOW}🔧 Setting up script permissions...${NC}"
chmod +x automate_pipeline.py
chmod +x run_dashboard.py

# Check essential files
echo ""
echo -e "${YELLOW}🔍 Checking essential files...${NC}"
ESSENTIAL_FILES=(
    "dashboard.py"
    "requirements.txt"
    "automate_pipeline.py"
    "run_dashboard.py"
)

MISSING_FILES=()
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file${NC}"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -ne 0 ]; then
    echo -e "${RED}❌ Missing essential files: ${MISSING_FILES[*]}${NC}"
    echo "Please ensure all required files are present"
    exit 1
fi

# Prepare pipeline arguments
PIPELINE_ARGS=""
if [ "$DASHBOARD_ONLY" = true ]; then
    PIPELINE_ARGS="--dashboard-only"
fi
PIPELINE_ARGS="$PIPELINE_ARGS --port $PORT"

# Run the automated pipeline
echo ""
echo -e "${YELLOW}🚀 Starting automated pipeline...${NC}"
echo -e "${BLUE}Arguments: $PIPELINE_ARGS${NC}"
echo ""

# Run the pipeline
python3 automate_pipeline.py $PIPELINE_ARGS

# Check exit status
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo -e "${BLUE}📱 Dashboard URL: http://localhost:$PORT${NC}"
    echo -e "${BLUE}🌍 Network URL: http://10.106.6.133:$PORT${NC}"
    echo ""
    echo -e "${YELLOW}💡 Next steps:${NC}"
    echo "  • Open the dashboard URL in your browser"
    echo "  • Use Ctrl+C to stop the dashboard when done"
    echo "  • Run './deploy.sh --dashboard-only' to restart just the dashboard"
    echo "  • Run './deploy.sh' to refresh all data and restart"
else
    echo ""
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}❌ DEPLOYMENT FAILED${NC}"
    echo -e "${RED}================================================${NC}"
    echo "Check the error messages above for details"
    exit 1
fi
