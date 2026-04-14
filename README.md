# 🏠 RV Agent Room

![RV Agent Room Preview](preview.png)

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
├── setup.sh            # 1-click setup — run once after cloning
├── agent_log.json      # Activity log (auto-generated, cleared daily)
├── agent_grid.json     # Wall layout (saved from editor)
└── character/          # All sprites and background image
```

---

## Quick Setup (1-click)

```bash
git clone https://github.com/roneya/Agent-room.git
cd Agent-room
bash setup.sh
```

That's it. `setup.sh` will:
- Detect where you cloned the repo
- Write `.claude/settings.local.json` with the correct paths for your machine
- Start `agent_server.py` on `http://localhost:7788`
- Open `index.html` in your browser

From then on, every time you open Claude Code in this folder the hooks auto-start everything.

#### What the hooks do

| Hook | When it fires | What it does |
|---|---|---|
| `SessionStart` | When you open Claude Code | Starts the server, opens the browser |
| `PreToolUse` | Before every tool Claude uses | Logs the tool → moves the character |
| `Stop` | When the session ends | Sends character to sofa (`done`) |
| `Notification` | When Claude finishes and notifies | Sends character to coffee (`waiting`) |

> `settings.local.json` is machine-specific and gitignored — `setup.sh` generates it fresh for each user.

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

## How the GitHub Pages Version Works

The project is hosted at **[https://roneya.github.io/Agent-room/](https://roneya.github.io/Agent-room/)**

> ⚠️ GitHub Pages only hosts the UI. The live character movement still requires your local server running.

Here's what's actually happening:

```
GitHub Pages ──serves──► your browser (the HTML/JS/assets)
                              │
                              └──fetches──► localhost:7788 (YOUR machine)
                                               │
                                         agent_server.py running locally
```

- **GitHub Pages** just delivers the HTML file — like a waiter bringing a menu
- **Your browser** runs the code and calls `localhost:7788` for live data
- **`localhost` always means your own machine**, regardless of what URL you opened

So if you open the GitHub Pages link on your Mac while `agent_server.py` is running, the character moves in real time — because your browser is silently pulling data from your local server.

If someone else opens the same link on their machine, they'll see the room frozen with an **offline** status — because their `localhost:7788` has nothing running.

**This means:** GitHub Pages is a shareable preview. Your local machine is the engine. By default, `launch.sh` opens your local `index.html` so it works offline and without any GitHub dependency.

---

## Requirements

- Python 3 (for `agent_server.py` and `hook.py`)
- Claude Code CLI
- A modern browser

No npm. No dependencies. No build step.

---

## Credits

Built by [Rohan Vidhate](https://www.linkedin.com/in/iamrohanvidhate/)
