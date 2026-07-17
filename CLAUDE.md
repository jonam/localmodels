# localcode

A local-first code generation CLI that orchestrates Ollama models (primarily Qwen3-Coder) to execute multi-file software projects from high-level specifications. Think of it as Claude Code for local models, with a hybrid architecture that compensates for the limitations of smaller models.

## Architecture

**Single-file Python CLI** (`localcode`) with no dependencies beyond Python 3 and Ollama.

### The Hybrid Model Problem

Qwen3-Coder (30B) is capable at isolated coding tasks but struggles with:
- Large context windows (starts hallucinating, forgets its task)
- Cross-file consistency (wrong port numbers, mismatched security groups, duplicate resource names)
- Planning and decomposition of big projects

The solution: use each model where it's strong.

### Three Phases

1. **Plan** — Sonnet (via AWS Bedrock) reads the project spec (typically a PDF), decomposes it into atomic tasks with dependencies, and produces a sequenced execution plan. Each task is one file creation or edit.

2. **Run** — Qwen picks up tasks one at a time via Ollama. The orchestrator feeds it minimal context (the task title, completed tasks summary, and pre-loaded project files). After each task, `verify_task()` runs syntax/reference checks. Failed tasks retry up to 3 times with the error fed back.

3. **Reconcile** — Sonnet reads all generated files together, identifies cross-module inconsistencies (wrong references, mismatched ports, missing security groups), and emits surgical fix tasks. These are appended to the plan and handed back to Qwen. Multiple reconcile rounds run until stability.

### Verification System

`verify_task()` runs after each task to catch errors early:
- Python: `ast.parse` (syntax only)
- JavaScript/Node: `node --check`
- TypeScript: single-file `tsc --noEmit`, plus project-wide check filtered against baseline
- Terraform: reference resolution check (verifies all `resource.name` references point to defined resources)

**Baseline error filtering**: Before each task runs, `collect_baseline_errors()` snapshots all pre-existing project-wide validation errors. After the task, only *new* errors (not in the baseline) cause failure. This prevents Task N from failing due to unresolved references that Task N+5 will create.

## Key Commands

```
/plan <file>          Create execution plan from a PDF/document
/plan run             Execute tasks sequentially
/plan status          Show progress
/plan reconcile       Run Sonnet cross-file consistency check
/plan hint <text>     Give Qwen a fix hint for a failed task and retry
/plan retry           Retry failed task from scratch
/plan rollback        Undo a failed task's changes
/plan reset [id]      Reset task(s) to pending
/plan nuke            Wipe all generated code and plan state
/undo [N]             Undo last N file changes
/mark <name>          Set a named checkpoint
/rollback <name>      Revert to a checkpoint
/cost                 Show token usage and estimated savings vs Claude
/model [name]         Show or switch model
/fast                 Toggle between full and fast model
```

## Design Principles

- Every file change is recorded in undo history with before-state snapshots
- User permission is requested before writing/editing/running anything
- Token usage is tracked per-call and cumulatively, with cost comparison to Claude
- Tasks are persisted to `.localcode/plan.json` — sessions can resume across restarts
- Context is kept small: project files are pre-loaded once, task prompts are self-contained
- The agent loop supports ESC-to-interrupt mid-generation

## File Layout

```
localcode           Single Python script (the entire CLI)
setup.sh            Ollama/model install helper
.localcode/         Per-project state (plan.json, history, marks)
```

## Development Notes

- No external Python packages — only stdlib + Ollama HTTP API + optional AWS Bedrock for Sonnet
- Tool calls are parsed from Qwen's raw text output (it doesn't support native function calling reliably)
- The `compact_messages()` function trims conversation history to stay within Qwen's context limit
- Reconciliation prompt is carefully structured to emit JSON tasks that match the plan schema
