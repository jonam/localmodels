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

## Plan System

Turn any project document (PDF, MD, TXT) into a fully executed codebase:

```bash
./localcode
> /plan project-spec.pdf    # Sonnet decomposes into 30-60 file-level tasks
> /plan run                  # QWEN executes tasks one at a time
```

### Plan Commands

| Command | Description |
| --- | --- |
| `/plan <file>` | Create execution plan from a document |
| `/plan status` | Show progress |
| `/plan run` | Start/resume task execution |
| `/plan reconcile` | Manually trigger cross-module analysis |
| `/plan hint <text>` | Give a fix hint for a failed task |
| `/plan retry` | Reset failed task and retry |
| `/plan rollback` | Undo current task's changes |
| `/plan done N` | Manually mark task N as done |
| `/plan reset [N]` | Reset task N (or all) to pending |
| `/plan split` | Break vague tasks into concrete sub-tasks |
| `/plan nuke` | Tear down infra + delete files + wipe plan |

### Hybrid Architecture: Sonnet + QWEN

The plan system uses a hybrid approach that compensates for local model limitations:

```
                    ┌─────────────────────────┐
                    │  Sonnet (via Bedrock)    │
                    │  • Decomposes PDF → tasks│
                    │  • Cross-module analysis │
                    │  • Surgical fix tasks    │
                    └───────────┬─────────────┘
                                │
              ┌─────────────────▼──────────────────┐
              │         QWEN (local, free)          │
              │  • Executes 1 task at a time        │
              │  • Writes/edits exactly 1 file      │
              │  • Syntax-validated after each task  │
              └────────────────────────────────────┘
```

**The problem:** QWEN executes tasks independently with no cross-file visibility. Task 25 might create a Lambda that sends data on port 8080, while task 24 created an EC2 server listening on port 5000.

**The solution — automatic reconciliation:** After all tasks complete, Sonnet reads ALL generated files together and detects:
- Port mismatches between services
- API contract disagreements (caller sends X, receiver expects Y)
- Dead code using deprecated services
- Duplicate/conflicting implementations
- Missing imports or environment variables
- Dependency version issues

Sonnet then emits **surgical fix tasks** with exact old_text → new_text edits that QWEN applies mechanically (no analysis required from the local model).

This cycle repeats automatically until Sonnet reports zero issues:

```
/plan run
  └→ QWEN executes tasks 1-60
  └→ Sonnet reconcile pass 1: finds 12 issues → emits tasks 61-72
  └→ QWEN executes fix tasks 61-72
  └→ Sonnet reconcile pass 2: finds 3 issues → emits tasks 73-75
  └→ QWEN executes fix tasks 73-75
  └→ Sonnet reconcile pass 3: 0 issues found ✓
  └→ "Reconciliation complete — all cross-module issues resolved."
```

### Dependency Detection

When a task produces a file that requires a tool for validation (e.g., `node` for `.js` files, `terraform` for `.tf` files), localcode will prompt you to install it:

```
  ⚠ 'node' is required to validate .js files but is not installed.
    Suggested install command: sudo apt install -y nodejs

  Install 'node' now? [Y]es / [n]o (abort plan):
```

Supports Linux (apt/dnf) and macOS (brew). If declined, the plan halts cleanly and can be resumed after manual installation.

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
- Generating functions and files from clear specs
- Multi-step code modifications
- Writing tests, scripts, configs
- Following patterns and conventions
- Tool use and agentic workflows
- Mechanical edits (exact find/replace)

It's weaker at (mitigated by Sonnet reconciliation):
- ~~Cross-file consistency~~ → caught by reconcile pass
- ~~Port/contract mismatches~~ → caught by reconcile pass
- ~~Dead code from conflicting approaches~~ → caught by reconcile pass
- Very large codebase reasoning (>10 files of context)
- Complex debugging with many moving parts
- Ambiguous requirements needing clarification
- Tasks requiring knowledge beyond training data

## Cost

| Phase | Model | Cost |
| --- | --- | --- |
| Plan creation | Sonnet (Bedrock) | ~$0.10-0.30 |
| Task execution | QWEN (local) | $0 |
| Reconcile pass | Sonnet (Bedrock) | ~$0.30-0.80 per pass |
| **Total for ~60 task project** | | **~$1-3** |
