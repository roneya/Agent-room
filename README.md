# 🏠 RV Agent Room

A real-time pixel-art room that visualizes what your Claude Code agent is doing — live, as it happens. No extra tokens. No API calls. Pure hook magic.

---

## What Is This?

Every time Claude uses a tool, a lightweight hook script fires in the background. It reads the tool name, maps it to an activity state, and logs it to a local JSON file. A browser-based pixel-art room polls that file and animates a character walking to the matching station.

**Zero tokens consumed. Zero prompts sent. It all runs locally.**

---

## How It Works

```
Claude uses a tool
      ↓
hook.py fires (PreToolUse hook)
      ↓
Maps tool name → state → logs to agent_log.json
      ↓
agent_server.py serves the log on localhost:7788
      ↓
index.html polls every 1s → character walks to station
```

---

## The 8 Stations

| Station | State | Triggered By |
|---|---|---|
| 💻 **Laptop** | `coding` | `Edit`, `Write`, `NotebookEdit`, `EnterWorktree`, `ExitWorktree` |
| 📚 **Bookshelf** | `reading` | `Read`, `Grep`, `Glob`, `WebFetch`, `WebSearch` |
| 🏃 **Treadmill** | `running` | `Bash`, `RemoteTrigger` |
| 🖊️ **Blackboard** | `thinking` | `Agent`, `TaskCreate`, `TaskUpdate`, `TaskGet`, `TaskList`, `TaskStop`, `TaskOutput`, `TodoWrite` |
| ♟️ **Chess Table** | `chess` | `Skill`, `EnterPlanMode`, `ExitPlanMode`, `CronCreate`, `CronDelete`, `CronList` |
| ☕ **Coffee** | `waiting` | `ToolSearch`, session notification |
| 🧊 **Fridge** | `fridge` | Any `mcp__*` tool (all MCP server calls) |
| 🛋️ **Sofa** | `done` | `AskUserQuestion`, session end |

Each station has its own animation — the character sits, writes, walks on the treadmill, naps on the sofa, opens the fridge, and more.

---

## Live Caption

Below the status indicator in the top-left corner, a small caption updates with a human-readable description of what Claude is doing:

| State | Caption |
|---|---|
| coding | I'm taking notes... |
| reading | I'm researching... |
| thinking | I'm thinking... |
| running | I'm running a command... |
| chess | Planning my move... |
| waiting | Fetching something... |
| fridge | Grabbing a tool... |
| done | All done! |
| coffee | Waiting for you... |

---

## Project Files

```
room/
├── index.html          # Pixel-art room (the visual)
├── hook.py             # Hook script — maps tools to states
├── agent_server.py     # Local HTTP server (port 7788)
├── launch.sh           # Auto-starts server + opens browser
├── agent_log.json      # Activity log (auto-generated)
├── agent_grid.json     # Wall layout (saved from editor)
└── character/          # All sprites and background image
```

---

## How to Set It Up

### 1. Clone the repo

```bash
git clone https://github.com/roneya/Agent-room.git
cd Agent-room
```

### 2. Add the hooks to Claude Code settings

This is the **most important step**. The room only works if Claude Code knows to call `hook.py` on every tool use.

Open or create `.claude/settings.local.json` inside your project folder and add:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash /YOUR/PATH/TO/room/launch.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /YOUR/PATH/TO/room/hook.py --state done"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /YOUR/PATH/TO/room/hook.py --state waiting"
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
            "command": "python3 /YOUR/PATH/TO/room/hook.py"
          }
        ]
      }
    ]
  }
}
```

> Replace `/YOUR/PATH/TO/room/` with the actual absolute path where you cloned the repo.

#### What each hook does

| Hook | When it fires | What it does |
|---|---|---|
| `SessionStart` | When you open Claude Code | Starts the server, opens the browser |
| `PreToolUse` | Before every tool Claude uses | Logs the tool → moves the character |
| `Stop` | When the session ends | Sends character to sofa (`done`) |
| `Notification` | When Claude finishes and notifies | Sends character to coffee (`waiting`) |

> **Note:** `settings.local.json` is gitignored by Claude Code by default — each user sets their own absolute paths locally.

### 3. Start Claude Code

Open Claude Code in any project. The room will:
- Auto-start the server on `http://localhost:7788`
- Open `index.html` in your browser
- Start animating immediately as Claude works

---

## Wall Editor

The room has a built-in wall editor to block off areas so the character navigates around them using A* pathfinding.

- Press **`E`** — toggle edit mode (crosshair cursor)
- **Left-click / drag** — paint walls
- **Right-click / drag** — erase walls
- Press **`D`** — toggle debug grid overlay
- Press **`E`** again — exit edit mode

Walls are saved to `agent_grid.json` via the local server and persist across sessions.

---

## Requirements

- Python 3 (for `agent_server.py` and `hook.py`)
- Claude Code CLI
- A modern browser

No npm. No dependencies. No build step.

---

## Credits

Built by [Rohan Vidhate](https://www.linkedin.com/in/iamrohanvidhate/)
