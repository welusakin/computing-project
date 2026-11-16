# System-Level File Manager

A modular C command-line file manager built around POSIX file and directory APIs. It demonstrates how a small utility can parse commands, call operating-system interfaces, check return values, and explain failures without delegating the work to a shell.

## Features

- `pwd`, `cd`, and `ls` for current-directory navigation and listing
- `mkdir` and `touch` for creating directories and files
- `cat` for reading a file through `open`/`read`/`write`
- `cp` for buffered file copying, with same-file detection and permission preservation
- `mv` using `rename`
- `rm` with an interactive confirmation; it removes a single entry and does not recurse into directories
- `help` and `exit`
- Explicit checks for system-call failures, interrupted reads/writes, invalid argument counts, and end-of-file

The command parser accepts whitespace-separated paths; paths containing spaces are outside this small command-line interface. It does not execute shell commands. `rm` asks before unlinking, and directory removal is intentionally unsupported.

## Build and run

On Linux or macOS with a C compiler and `make`:

```bash
make
./file-manager
```

Try a short session:

```text
help
pwd
ls .
mkdir demo
cd demo
touch notes.txt
cat notes.txt
cd ..
rm demo/notes.txt
```

`make clean` removes the compiled executable.

## Implementation map

- `src/file_manager.c` contains the prompt loop, command parser, command handlers, and checked low-level I/O helpers.
- `Makefile` builds the program with warnings enabled.

## System interfaces used

The implementation uses `open`, `read`, `write`, `close`, `stat`, `fstat`, `fchmod`, `mkdir`, `unlink`, `rename`, `chdir`, and `getcwd`, plus `opendir`/`readdir` for directory enumeration. Each failing operation reports the operation and path along with the system error message.

This is an independently rebuilt version based on the project scope in my notes. The original class submission files were not available.
