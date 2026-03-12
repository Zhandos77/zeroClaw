#!/bin/bash
# News fetcher script
# Fetches news from configured sources and outputs summary

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_SCRIPT="$WORKSPACE_DIR/utils/news_parser/test_parser.py"
OUTPUT_DIR="$WORKSPACE_DIR/data/news"
LOG_FILE="$OUTPUT_DIR/news_fetch_$(date +%Y%m%d_%H%M%S).log"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "📰 Starting news fetch at $(date)" | tee -a "$LOG_FILE"
echo "Working directory: $WORKSPACE_DIR" | tee -a "$LOG_FILE"

# Check Python dependencies
echo "🔍 Checking Python dependencies..." | tee -a "$LOG_FILE"

if ! python3 -c "import feedparser" 2>/dev/null; then
    echo "Installing feedparser..." | tee -a "$LOG_FILE"
    pip3 install feedparser beautifulsoup4 requests --quiet
fi

# Run the Python parser
echo "🚀 Running news parser..." | tee -a "$LOG_FILE"

cd "$WORKSPACE_DIR"
python3 "$PYTHON_SCRIPT" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ News fetch completed successfully at $(date)" | tee -a "$LOG_FILE"
    
    # Generate summary
    LATEST_JSON=$(ls -t "$OUTPUT_DIR"/*.json 2>/dev/null | head -1)
    if [ -n "$LATEST_JSON" ]; then
        COUNT=$(python3 -c "
import json
with open('$LATEST_JSON', 'r') as f:
    data = json.load(f)
print(data.get('total_items', 0))
" 2>/dev/null || echo "0")
        
        echo "📊 Fetched $COUNT news items" | tee -a "$LOG_FILE"
        echo "💾 Latest data: $LATEST_JSON" | tee -a "$LOG_FILE"
    fi
else
    echo "❌ News fetch failed with exit code $EXIT_CODE" | tee -a "$LOG_FILE"
fi

echo "📋 Log saved to: $LOG_FILE" | tee -a "$LOG_FILE"

exit $EXIT_CODE