#!/bin/bash
# Auto-launcher for the Agent Tracker Room
# Called by Claude Code SessionStart hook

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Start agent_server.py if not already running on port 7788
if ! lsof -i :7788 -sTCP:LISTEN -t > /dev/null 2>&1; then
  python3 "$PROJECT_DIR/agent_server.py" > /dev/null 2>&1 &
  echo "Started agent_server.py (PID $!)"
else
  echo "agent_server.py already running on :7788"
fi

# Open index.html in default browser
open "file://$PROJECT_DIR/index.html"
