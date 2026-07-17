# localcode

A terminal coding agent like Claude Code, but runs locally with Qwen3-Coder via Ollama. No API keys, no cost, works offline.

The agent reads files, writes files, edits code, runs commands, and iterates - not just chat.

## Setup

```bash
./setup.sh
```

Downloads Ollama and the model (~19GB for qwen3-coder:30b on first run).

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

The agent loop: prompt → model decides actions → executes tools → feeds results back → repeats until done (up to 10 iterations).

## Commands

| Command | Description |
| --- | --- |
| `/clear` | Reset conversation |
| `/model [name]` | Show or switch model |
| `/fast` | Toggle between full and fast model |
| `/help` | Show commands |
| `/quit` | Exit |

## Environment

| Variable | Default | Description |
| --- | --- | --- |
| `LOCALCODE_MODEL` | auto-detected | Model to use (override auto-detection) |
| `LOCALCODE_FAST_MODEL` | `qwen3:8b` | Fast model for `/fast` toggle |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama URL |

## Model Selection

The setup script auto-detects RAM and picks the best model:

| RAM | Default Model | Disk | Notes |
|-----|--------------|------|-------|
| 16-32 GB | `qwen3:14b` | ~9 GB | Dense model, good reasoning |
| 32+ GB | `qwen3-coder:30b` | ~19 GB | MoE (3B active), optimized for tool-use |
| < 16 GB | `qwen3:8b` | ~5 GB | Fast, lighter tasks |

Override with: `LOCALCODE_MODEL=qwen3:14b ./localcode`

Toggle between full and fast model at runtime with `/fast`.

### Why Qwen3-Coder?

**Qwen3-Coder-30B** is a Mixture-of-Experts (MoE) model with only 3B parameters active per token, despite having 30B total parameters. This matters for CPU inference:

- **Faster than dense 32B**: Only 3B params active → much less computation per token
- **Native tool-calling**: Trained specifically for agentic workflows with structured tool_calls
- **256K context window**: Enough for multi-file projects without truncation
- **Coding-specialized**: 70.6% on SWE-Bench Verified, 358 programming languages

Compared to the older Qwen2.5-Coder-32B:
- ~5-10x faster inference on CPU (3B active vs 32B dense)
- Better structured tool-use (native support vs bolted-on)
- Larger context window (256K vs 128K)

## Requirements

- Linux or macOS, 16+ GB RAM (32+ GB recommended for qwen3-coder:30b)
- Python 3.9+
- ~5-19 GB disk depending on model size

## Performance on CPU-only (no GPU)

On a 64GB RAM / 16-thread CPU (e.g., Intel i7-11800H):
- **qwen3:8b**: ~15-25 tok/s — snappy for quick tasks
- **qwen3:14b**: ~8-12 tok/s — good balance
- **qwen3-coder:30b (MoE)**: ~10-20 tok/s — fast due to only 3B active params

The MoE architecture means qwen3-coder:30b is actually faster than a dense 14B model while being significantly smarter.

## Claude Code CLI + Local Models

**Note:** Claude Code CLI does not currently support pointing at arbitrary OpenAI-compatible endpoints like Ollama. It only supports Anthropic's own API, Amazon Bedrock, Google Vertex AI, and Microsoft Foundry as providers.

If you want a Claude Code-like experience with local models, use this `./localcode` agent — it's purpose-built for local Ollama models with robust tool-call parsing that handles the quirks of local model outputs.

## Limitations

Qwen3-Coder is good at:
- Generating functions and files
- Multi-step code modifications
- Writing tests, scripts, configs
- Following patterns and conventions
- Tool use and agentic workflows
- Parallel function calls

It's weaker at:
- Very large codebase reasoning (>10 files of context)
- Complex debugging with many moving parts
- Ambiguous requirements needing clarification
- Tasks requiring knowledge beyond training data
