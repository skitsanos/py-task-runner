import concurrent.futures
import datetime
import subprocess
import os
import argparse


def run_task(command):
    """Function to run a command in a subprocess."""
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return f"{result.stdout.decode().strip()}"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.decode().strip()}"


def main():
    # check command line arguments
    parser = argparse.ArgumentParser(
        prog='task-runner',
        description='Run a list of commands in parallel.',
        epilog='Example usage: python task-runner.py -f /path/to/file.txt -t cpu',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-f", "--file", type=str, help="path to file")
    parser.add_argument("-t", "--type", type=str, help='Type of task pool (cpu or io)', default='cpu')
    args = parser.parse_args()

    if not args.file or not args.type:
        parser.print_help()
        exit(1)

    # exit if there is no file provided
    if not args.file:
        print("Please provide a file path.")
        exit(1)

    # exit if the file does not exist
    if not os.path.exists(args.file):
        print(f"File {args.file} does not exist.")
        exit(1)

    # set number of workers for the task pool
    num_cores = os.cpu_count()

    if args.type == "cpu":
        num_workers = num_cores
    else:  # Assuming I/O-bound tasks
        num_workers = num_cores * 2  # Adjust this multiplier based on testing

    # file should have each task on a new line
    with open(args.file, 'r') as f:
        commands = f.read().splitlines()

        # remove empty lines
        commands = [cmd for cmd in commands if cmd.strip()]

        print(f"Running {len(commands)} tasks with {num_workers} workers.")

        # Using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            start_times = {cmd: datetime.datetime.now() for cmd in commands}

            # Submit tasks to the executor
            future_to_command = {executor.submit(run_task, cmd): cmd for cmd in commands}

            # Handling results as they complete
            for future in concurrent.futures.as_completed(future_to_command):
                end_time = datetime.datetime.now()
                command = future_to_command[future]
                start_time = start_times[command]
                exec_time = end_time - start_time

                try:
                    data = future.result()
                    timestamp = end_time.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{timestamp} {exec_time} {command}: {data}")
                except Exception as exc:
                    print(f"{command} generated an exception: {exc}")


if __name__ == "__main__":
    main()
