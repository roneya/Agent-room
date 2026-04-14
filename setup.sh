#!/bin/bash
# 1-click setup for Agent Tracker Room
# Run once after cloning: bash setup.sh

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
echo "Setting up Agent Tracker Room at: $PROJECT_DIR"

# Make scripts executable
chmod +x "$PROJECT_DIR/launch.sh"
chmod +x "$PROJECT_DIR/hook.py"
chmod +x "$PROJECT_DIR/agent_server.py"

# Write .claude/settings.local.json with paths for this machine
mkdir -p "$PROJECT_DIR/.claude"
cat > "$PROJECT_DIR/.claude/settings.local.json" << EOF
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash $PROJECT_DIR/launch.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $PROJECT_DIR/hook.py --state done"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 $PROJECT_DIR/hook.py --state waiting"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "python3 $PROJECT_DIR/hook.py"
          }
        ]
      }
    ]
  },
  "permissions": {
    "allow": [
      "Bash(python3:*)",
      "Bash(ls:*)"
    ]
  }
}
EOF

echo "Hooks configured."

# Start server + open browser
bash "$PROJECT_DIR/launch.sh"

echo ""
echo "Done! Open Claude Code in this folder and your tracker will auto-start."
