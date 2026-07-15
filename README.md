# localcode

A terminal coding agent like Claude Code, but runs locally with Qwen2.5-Coder 7B via Ollama. No API keys, no cost, works offline.

The agent reads files, writes files, edits code, runs commands, and iterates - not just chat.

## Setup

```bash
./setup.sh
```

Downloads Ollama and the model (~4GB first time).

## Usage

```bash
./localcode
```

Then tell it what to build:

```
> create a Next.js app with a /api/users endpoint that queries postgres
> add error handling to src/utils.py
> write a bash script to deploy this to AWS
> refactor this component to use React hooks - read src/components/Form.tsx
```

The agent will read your files, make changes, and run commands directly. You don't need to copy-paste code.

## How It Works

The model has access to tools:

| Tool | What it does |
| --- | --- |
| `read_file` | Read existing files |
| `write_file` | Create or overwrite files |
| `edit_file` | Make targeted edits (find/replace) |
| `run_command` | Run shell commands (build, test, install) |
| `list_files` | Browse project structure |
| `search_files` | Grep for patterns |

The agent loop: prompt → model decides actions → executes tools → feeds results back → repeats until done (up to 15 iterations).

## Commands

| Command | Description |
| --- | --- |
| `/clear` | Reset conversation |
| `/model [name]` | Show or switch model |
| `/help` | Show commands |
| `/quit` | Exit |

## Environment

| Variable | Default | Description |
| --- | --- | --- |
| `LOCALCODE_MODEL` | `qwen2.5-coder:7b` | Model to use |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama URL |

## Requirements

- macOS Apple Silicon, 16 GB unified memory
- Python 3.9+ (pre-installed on macOS)
- ~4 GB disk for the model

## Limitations

7B models are good at:
- Generating functions and files
- Editing existing code
- Writing tests, scripts, configs
- Following clear instructions

They're weaker at:
- Multi-file architectural changes
- Complex debugging
- Understanding very large codebases
- Ambiguous requirements
