import argparse
import concurrent.futures
import datetime
import os
import shlex
import subprocess
import sys


def run_task(command, use_shell=False, timeout=None):
    """Run a command and return stdout, stderr, and exit code."""
    try:
        cmd = command if use_shell else shlex.split(command)
        result = subprocess.run(
            cmd,
            shell=use_shell,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout.decode().strip(),
            "stderr": result.stderr.decode().strip(),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired as exc:
        return {"stdout": "", "stderr": f"timeout after {exc.timeout}s", "returncode": -1}


def main():
    # check command line arguments
    parser = argparse.ArgumentParser(
        prog='task-runner',
        description='Run a list of commands in parallel.',
        epilog='Example usage: python task-runner.py -f /path/to/file.txt -t cpu',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-f", "--file", type=str, required=True, help="path to file with commands (one per line)")
    parser.add_argument("-t", "--type", choices=["cpu", "io"], default="cpu", help="type of task pool")
    parser.add_argument("--timeout", type=float, default=None, help="per-command timeout in seconds")
    parser.add_argument("--shell", action="store_true", help="run commands through the shell (allows pipes, redirection)")
    args = parser.parse_args()

    # exit if the file does not exist
    if not os.path.exists(args.file):
        print(f"File {args.file} does not exist.")
        sys.exit(1)

    # set number of workers for the task pool
    num_cores = os.cpu_count() or 1

    if args.type == "cpu":
        num_workers = max(1, num_cores)
        executor_cls = concurrent.futures.ProcessPoolExecutor
    else:  # I/O-bound tasks
        num_workers = max(1, min(32, num_cores * 2))
        executor_cls = concurrent.futures.ThreadPoolExecutor

    # file should have each task on a new line
    with open(args.file, 'r') as f:
        commands = f.read().splitlines()

        # remove empty lines
        commands = [cmd for cmd in commands if cmd.strip() and not cmd.strip().startswith('#')]

        if not commands:
            print("No runnable commands found in file.")
            sys.exit(0)

        print(f"Running {len(commands)} tasks with {num_workers} workers.")

        with executor_cls(max_workers=num_workers) as executor:
            future_to_meta = {}

            for cmd in commands:
                future = executor.submit(run_task, cmd, args.shell, args.timeout)
                future_to_meta[future] = {
                    "command": cmd,
                    "start": datetime.datetime.now(),
                }

            for future in concurrent.futures.as_completed(future_to_meta):
                end_time = datetime.datetime.now()
                meta = future_to_meta[future]
                exec_time = end_time - meta["start"]

                try:
                    result = future.result()
                    timestamp = end_time.strftime("%Y-%m-%d %H:%M:%S")
                    status = "OK" if result["returncode"] == 0 else f"FAIL({result['returncode']})"
                    stderr_part = f" | stderr: {result['stderr']}" if result['stderr'] else ""
                    stdout_part = result['stdout'] if result['stdout'] else "<no output>"
                    print(f"{timestamp} {exec_time} [{status}] {meta['command']} => {stdout_part}{stderr_part}")
                except Exception as exc:
                    print(f"{meta['command']} generated an exception: {exc}")


if __name__ == "__main__":
    main()
