# py-task-runner

Multi-threaded task runner in Python

This Python application is designed to efficiently manage and execute a large batch of tasks in parallel. Utilizing the
power of multi-threading, it reads a list of commands from a file and executes them concurrently, optimizing the use of
system resources. The application is particularly adept at handling both CPU-bound and I/O-bound tasks, dynamically
adjusting the number of worker threads based on the nature of the tasks and the capabilities of the underlying hardware.

## Key Features

- **Concurrent Task Execution**: Leverages concurrent.futures.ThreadPoolExecutor for executing multiple tasks in
  parallel, significantly improving the efficiency for large batches of tasks.
- **Robust Error Handling**: Each task is executed in a separate subprocess with comprehensive error handling, ensuring
  the overall process continues smoothly even if individual tasks fail.
- **Detailed Logging**: Outputs detailed logs for each task, including a timestamp, execution time, command, and the
  result or error message, aiding in easy monitoring and debugging.
- **Command-Line Interface**: Offers a simple and intuitive command-line interface for specifying the file containing
  the tasks and the type of tasks, enhancing user convenience and flexibility.

## Usage

The application is designed to be user-friendly and can be easily executed from the command line. Users can specify the
path to the file containing the tasks and the type of tasks (CPU-bound or I/O-bound). The file should contain one
command per line.

```shell
python task-runner.py -f /path/to/file.txt -t [cpu/io]
```

```
options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to file
  -t TYPE, --type TYPE  Type of task pool (cpu or io)
```

## Getting Started

To get started with this application, clone the repository, ensure Python 3.x is installed on your system, and run the
script with the desired parameters.

This tool is ideal for scenarios where you need to run multiple commands or scripts simultaneously and efficiently, such
as batch processing, data analysis, or automated testing environments.