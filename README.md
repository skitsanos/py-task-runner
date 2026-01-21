# py-task-runner

Parallel task runner in Python.

This tool reads commands from a file and runs them in parallel with sensible defaults for CPU vs. I/O workloads, safer
command execution, and clear per-task logging.

## Key Features
- CPU/I/O aware executors: `ProcessPoolExecutor` for CPU (`-t cpu`), `ThreadPoolExecutor` for I/O (`-t io`), worker
  counts derived from core count (min 1, IO capped at 32).
- Shell-safe by default: commands are parsed with `shlex` and run without a shell; opt in to shell behavior with
  `--shell` when you need pipes or redirection.
- Timeouts: optional `--timeout` (seconds) to abort hung commands; reported as `FAIL(-1)`.
- Robust logging: timestamp, duration, status (`OK`/`FAIL(code)`), command, stdout placeholder, and stderr when present.
- Clean inputs: blank lines and `#` comments in the commands file are ignored.

## Usage
Provide a file with one command per line:
```shell
python3 task-runner.py -f /path/to/file.txt -t [cpu|io] [--timeout 30] [--shell]
```

Options:
```
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to file with commands (one per line)
  -t {cpu,io}, --type {cpu,io}
                        type of task pool
  --timeout TIMEOUT     per-command timeout in seconds
  --shell               run commands through the shell (allows pipes, redirection)
```

Notes:
- Default is shell-less execution; use `--shell` only when needed.
- For CPU-heavy commands, prefer `-t cpu`; for I/O-heavy commands, prefer `-t io`.
- If the commands file is empty (after comments/blank lines), the runner exits cleanly.

### When to use `--shell`
- **Use it** if the command relies on shell features such as pipes (`|`), redirection (`>`, `>>`, `<`), `&&`/`||`
  chaining, globbing (`*.csv`), or environment variable expansion like `$HOME` within the command string.
- **Skip it (default)** when the command is a single executable with arguments (e.g., `ffmpeg -i in.mp4 out.mp3`,
  `python3 script.py --flag`). Shell-less mode avoids injection risks and removes reliance on a specific shell.

#### Examples
Shell-less (default), safe argument parsing:
```
python3 process.py --input data/file1.csv --output out/file1.json
ffmpeg -i video.mp4 -vf scale=1280:-1 out.mp4
```
Run with:
```
python3 task-runner.py -f tasks_to_run.txt -t cpu
```

Shell-required (use `--shell`) because of pipes/redirection/globbing:
```
cat data/*.log | grep ERROR > errors.txt
python3 scrape.py siteA && python3 scrape.py siteB
```
Run with:
```
python3 task-runner.py -f tasks_to_run.txt -t io --shell
```

## Environment & Tasks
The repo includes a `Taskfile.yaml` with helpful tasks (requires `uv`):
- `task venv` — create `.venv` with uv.
- `task install` — activate `.venv`, upgrade pip, install `requirements.txt` (only if the file exists).
- `task drop` — activate `.venv` and uninstall all packages.

## Worker Policy
- CPU: up to `os.cpu_count()` workers via processes.
- I/O: up to `min(32, os.cpu_count() * 2)` workers via threads.

## Building a Binary (optional)
You can bundle the runner with PyInstaller:
```shell
task venv && . .venv/bin/activate
pip install pyinstaller
pyinstaller --onefile task-runner.py
```
The executable will appear in `dist/`.

## Example commands file
```
# simple demo
echo "hello"
sleep 1 && echo "done"
```

## When to use it
- **Batching shell commands**: run large lists of CLI jobs (data conversions, API calls, git ops) without writing glue.
- **Data/ML preprocessing**: fan out CPU-heavy transforms (e.g., image/audio feature extraction) with `-t cpu`.
- **I/O-heavy chores**: parallelize downloads/uploads, log processing, or ETL steps with `-t io`.
- **Smoke tests / checks**: execute many short validation scripts in parallel to shorten feedback loops.
- **Ops tooling**: drive repeated maintenance commands across hosts or services (especially when commands come from a generated list).
