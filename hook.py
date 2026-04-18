#!/usr/bin/env python3
"""
Claude Code pre_tool_use hook — project-local.
Reads tool name from stdin JSON and appends to agent_log.json
so agent_server.py can serve the full history to the room tracker.
"""
import json, sys, os, time

TOKEN_FILE    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token_state.json')
CONTEXT_LIMIT = 200_000  # claude-sonnet context window

# Log file lives next to this hook in the project folder
LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent_log.json')

TOOL_STATE_MAP = {
    # Coding / editing → Laptop
    'Edit':          'coding',
    'Write':         'coding',
    'NotebookEdit':  'coding',
    'EnterWorktree': 'coding',
    'ExitWorktree':  'coding',
    # Reading / research → Bookshelf
    'Read':          'reading',
    'Grep':          'reading',
    'Glob':          'reading',
    'WebFetch':      'reading',
    'WebSearch':     'reading',
    # Running commands → Treadmill
    'Bash':          'running',
    'RemoteTrigger': 'running',
    # Thinking / planning → Board
    'Agent':         'thinking',
    'TaskCreate':    'thinking',
    'TaskUpdate':    'thinking',
    'TaskGet':       'thinking',
    'TaskList':      'thinking',
    'TaskStop':      'thinking',
    'TaskOutput':    'thinking',
    'TodoWrite':     'thinking',
    # Strategy / skills → Chess
    'Skill':         'chess',
    'EnterPlanMode': 'chess',
    'ExitPlanMode':  'chess',
    'CronCreate':    'chess',
    'CronDelete':    'chess',
    'CronList':      'chess',
    # Fetching tool schemas → Coffee (waiting)
    'ToolSearch':    'waiting',
    # Waiting for user → Sofa
    'AskUserQuestion': 'done',
}

# Tool name prefixes → state (checked when exact match not found)
PREFIX_STATE_MAP = {
    'mcp__': 'fridge',   # any MCP server call → Fridge
}

def append_log(state, message=''):
    try:
        now = time.time()
        today = time.strftime('%Y-%m-%d', time.localtime(now))
        try:
            with open(LOG_FILE, 'r') as f:
                log = json.load(f)
            # Reset if the first entry is from a previous day
            if log:
                first_day = time.strftime('%Y-%m-%d', time.localtime(log[0]['ts']))
                if first_day != today:
                    log = []
        except (FileNotFoundError, json.JSONDecodeError):
            log = []
        entry = {'id': len(log), 'state': state, 'message': message, 'ts': now}
        log.append(entry)
        with open(LOG_FILE, 'w') as f:
            json.dump(log, f)
    except Exception:
        pass

def resolve_state(tool):
    if tool in TOOL_STATE_MAP:
        return TOOL_STATE_MAP[tool]
    for prefix, state in PREFIX_STATE_MAP.items():
        if tool.startswith(prefix):
            return state
    return 'coding'  # default

def update_token_state(transcript_path):
    """Read last assistant message usage from transcript and save token state."""
    try:
        usage = None
        with open(transcript_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if obj.get('type') == 'assistant':
                        u = obj.get('message', {}).get('usage')
                        if u:
                            usage = u
                except Exception:
                    pass
        if not usage:
            return
        used = (usage.get('input_tokens', 0)
              + usage.get('cache_creation_input_tokens', 0)
              + usage.get('cache_read_input_tokens', 0))
        pct_used      = round(used / CONTEXT_LIMIT * 100, 1)
        pct_remaining = round(100 - pct_used, 1)
        state = {'used': used, 'limit': CONTEXT_LIMIT,
                 'pct_used': pct_used, 'pct_remaining': pct_remaining,
                 'ts': time.time()}
        with open(TOKEN_FILE, 'w') as f:
            json.dump(state, f)
    except Exception:
        pass


def main():
    # Support: python3 hook.py --state done  (used by Stop hook)
    if len(sys.argv) == 3 and sys.argv[1] == '--state':
        try:
            data = json.load(sys.stdin)
            transcript = data.get('transcript_path', '')
            if transcript and os.path.exists(transcript):
                update_token_state(transcript)
        except Exception:
            pass
        append_log(sys.argv[2], sys.argv[2])
        return  # no stdout needed for Stop hook

    try:
        data = json.load(sys.stdin)
        tool = data.get('tool_name', '')
        state = resolve_state(tool)
        append_log(state, tool)
        # Extract real token usage from transcript
        transcript = data.get('transcript_path', '')
        if transcript and os.path.exists(transcript):
            update_token_state(transcript)
    except Exception:
        append_log('idle')

    # Always allow the tool to proceed
    print(json.dumps({'continue': True}))

if __name__ == '__main__':
    main()
