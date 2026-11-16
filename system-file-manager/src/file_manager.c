#define _POSIX_C_SOURCE 200809L

#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define INPUT_LIMIT 4096
#define COPY_BUFFER_SIZE 16384

static void report_error(const char *operation, const char *path) {
    int saved_errno = errno;
    if (path != NULL) {
        fprintf(stderr, "%s '%s': %s\n", operation, path, strerror(saved_errno));
    } else {
        fprintf(stderr, "%s: %s\n", operation, strerror(saved_errno));
    }
}

static bool write_all(int descriptor, const char *buffer, size_t length) {
    size_t offset = 0;
    while (offset < length) {
        ssize_t written = write(descriptor, buffer + offset, length - offset);
        if (written < 0 && errno == EINTR) {
            continue;
        }
        if (written <= 0) {
            return false;
        }
        offset += (size_t)written;
    }
    return true;
}

static int command_pwd(void) {
    char *directory = getcwd(NULL, 0);
    if (directory == NULL) {
        report_error("getcwd", NULL);
        return 1;
    }
    puts(directory);
    free(directory);
    return 0;
}

static int command_cd(const char *path) {
    const char *destination = path == NULL ? getenv("HOME") : path;
    if (destination == NULL) {
        fprintf(stderr, "cd: HOME is not set\n");
        return 1;
    }
    if (chdir(destination) < 0) {
        report_error("cd", destination);
        return 1;
    }
    return command_pwd();
}

static int command_ls(const char *path) {
    const char *directory_name = path == NULL ? "." : path;
    DIR *directory = opendir(directory_name);
    if (directory == NULL) {
        report_error("ls", directory_name);
        return 1;
    }
    errno = 0;
    struct dirent *entry;
    while ((entry = readdir(directory)) != NULL) {
        puts(entry->d_name);
        errno = 0;
    }
    if (errno != 0) {
        report_error("readdir", directory_name);
        (void)closedir(directory);
        return 1;
    }
    if (closedir(directory) < 0) {
        report_error("closedir", directory_name);
        return 1;
    }
    return 0;
}

static int command_mkdir(const char *path) {
    if (mkdir(path, 0755) < 0) {
        report_error("mkdir", path);
        return 1;
    }
    printf("Created directory: %s\n", path);
    return 0;
}

static int command_touch(const char *path) {
    int descriptor = open(path, O_WRONLY | O_CREAT, 0644);
    if (descriptor < 0) {
        report_error("touch", path);
        return 1;
    }
    if (close(descriptor) < 0) {
        report_error("close", path);
        return 1;
    }
    printf("Created or opened: %s\n", path);
    return 0;
}

static int command_cat(const char *path) {
    int descriptor = open(path, O_RDONLY);
    if (descriptor < 0) {
        report_error("cat", path);
        return 1;
    }
    char buffer[COPY_BUFFER_SIZE];
    for (;;) {
        ssize_t amount = read(descriptor, buffer, sizeof(buffer));
        if (amount < 0 && errno == EINTR) {
            continue;
        }
        if (amount < 0) {
            report_error("read", path);
            (void)close(descriptor);
            return 1;
        }
        if (amount == 0) {
            break;
        }
        if (!write_all(STDOUT_FILENO, buffer, (size_t)amount)) {
            report_error("write", "standard output");
            (void)close(descriptor);
            return 1;
        }
    }
    if (close(descriptor) < 0) {
        report_error("close", path);
        return 1;
    }
    return 0;
}

static int command_cp(const char *source, const char *destination) {
    int input = open(source, O_RDONLY);
    if (input < 0) {
        report_error("cp", source);
        return 1;
    }
    struct stat source_info;
    if (fstat(input, &source_info) < 0) {
        report_error("fstat", source);
        (void)close(input);
        return 1;
    }
    if (!S_ISREG(source_info.st_mode)) {
        fprintf(stderr, "cp: source must be a regular file: %s\n", source);
        (void)close(input);
        return 1;
    }
    struct stat destination_info;
    errno = 0;
    if (stat(destination, &destination_info) == 0 &&
        source_info.st_dev == destination_info.st_dev &&
        source_info.st_ino == destination_info.st_ino) {
        fprintf(stderr, "cp: source and destination refer to the same file\n");
        (void)close(input);
        return 1;
    }
    if (errno != 0 && errno != ENOENT) {
        report_error("stat", destination);
        (void)close(input);
        return 1;
    }

    int output = open(destination, O_WRONLY | O_CREAT | O_TRUNC, source_info.st_mode & 0777);
    if (output < 0) {
        report_error("cp", destination);
        (void)close(input);
        return 1;
    }
    if (fchmod(output, source_info.st_mode & 0777) < 0) {
        report_error("fchmod", destination);
        (void)close(input);
        (void)close(output);
        return 1;
    }

    char buffer[COPY_BUFFER_SIZE];
    bool success = true;
    for (;;) {
        ssize_t amount = read(input, buffer, sizeof(buffer));
        if (amount < 0 && errno == EINTR) {
            continue;
        }
        if (amount < 0) {
            report_error("read", source);
            success = false;
            break;
        }
        if (amount == 0) {
            break;
        }
        if (!write_all(output, buffer, (size_t)amount)) {
            report_error("write", destination);
            success = false;
            break;
        }
    }
    if (close(input) < 0) {
        report_error("close", source);
        success = false;
    }
    if (close(output) < 0) {
        report_error("close", destination);
        success = false;
    }
    if (!success) {
        (void)unlink(destination);
        return 1;
    }
    printf("Copied %s -> %s\n", source, destination);
    return 0;
}

static int command_mv(const char *source, const char *destination) {
    if (rename(source, destination) < 0) {
        report_error("mv", source);
        return 1;
    }
    printf("Moved %s -> %s\n", source, destination);
    return 0;
}

static int command_rm(const char *path) {
    struct stat info;
    if (lstat(path, &info) < 0) {
        report_error("rm", path);
        return 1;
    }
    if (S_ISDIR(info.st_mode)) {
        fprintf(stderr, "rm: directories are not supported; refusing to remove '%s'\n", path);
        return 1;
    }
    printf("Remove '%s'? [y/N] ", path);
    fflush(stdout);
    char *answer = NULL;
    size_t capacity = 0;
    ssize_t length = getline(&answer, &capacity, stdin);
    bool confirmed = length > 0 && (answer[0] == 'y' || answer[0] == 'Y');
    free(answer);
    if (!confirmed) {
        puts("Cancelled.");
        return 0;
    }
    if (unlink(path) < 0) {
        report_error("rm", path);
        return 1;
    }
    printf("Removed: %s\n", path);
    return 0;
}

static void print_help(void) {
    puts("Commands (paths are whitespace-separated; no shell commands are run):");
    puts("  pwd                 print the current directory");
    puts("  cd [directory]      change directory (defaults to HOME)");
    puts("  ls [directory]      list a directory");
    puts("  mkdir <directory>   create a directory");
    puts("  touch <file>        create a file if it does not exist");
    puts("  cat <file>          write a file's contents to the terminal");
    puts("  cp <source> <dest>  copy a regular file");
    puts("  mv <source> <dest>  rename or move a path");
    puts("  rm <file>           confirm, then remove one non-directory entry");
    puts("  help                show this help");
    puts("  exit                quit the file manager");
}

static int dispatch(char **tokens, size_t count, bool *should_exit) {
    const char *command = tokens[0];
    if (strcmp(command, "help") == 0) {
        if (count != 1) goto wrong_arguments;
        print_help();
    } else if (strcmp(command, "exit") == 0 || strcmp(command, "quit") == 0) {
        if (count != 1) goto wrong_arguments;
        *should_exit = true;
    } else if (strcmp(command, "pwd") == 0) {
        if (count != 1) goto wrong_arguments;
        return command_pwd();
    } else if (strcmp(command, "cd") == 0) {
        if (count > 2) goto wrong_arguments;
        return command_cd(count == 2 ? tokens[1] : NULL);
    } else if (strcmp(command, "ls") == 0) {
        if (count > 2) goto wrong_arguments;
        return command_ls(count == 2 ? tokens[1] : NULL);
    } else if (strcmp(command, "mkdir") == 0 || strcmp(command, "touch") == 0 ||
               strcmp(command, "cat") == 0 || strcmp(command, "rm") == 0) {
        if (count != 2) goto wrong_arguments;
        if (strcmp(command, "mkdir") == 0) return command_mkdir(tokens[1]);
        if (strcmp(command, "touch") == 0) return command_touch(tokens[1]);
        if (strcmp(command, "cat") == 0) return command_cat(tokens[1]);
        return command_rm(tokens[1]);
    } else if (strcmp(command, "cp") == 0 || strcmp(command, "mv") == 0) {
        if (count != 3) goto wrong_arguments;
        return strcmp(command, "cp") == 0
            ? command_cp(tokens[1], tokens[2])
            : command_mv(tokens[1], tokens[2]);
    } else {
        fprintf(stderr, "Unknown command: %s (type 'help')\n", command);
        return 1;
    }
    return 0;

wrong_arguments:
    fprintf(stderr, "Wrong number of arguments for '%s' (type 'help')\n", command);
    return 1;
}

int main(void) {
    char *line = NULL;
    size_t capacity = 0;
    bool should_exit = false;
    puts("System-Level File Manager — type 'help' for commands.");
    while (!should_exit) {
        char *directory = getcwd(NULL, 0);
        printf("%s> ", directory == NULL ? "?" : directory);
        free(directory);
        fflush(stdout);
        ssize_t length = getline(&line, &capacity, stdin);
        if (length < 0) {
            if (ferror(stdin)) {
                report_error("input", NULL);
                free(line);
                return 1;
            }
            break;
        }
        if ((size_t)length > INPUT_LIMIT) {
            fprintf(stderr, "Input line exceeds %d characters; ignored.\n", INPUT_LIMIT);
            continue;
        }
        char *tokens[4];
        size_t token_count = 0;
        char *save = NULL;
        for (char *token = strtok_r(line, " \t\r\n", &save);
             token != NULL;
             token = strtok_r(NULL, " \t\r\n", &save)) {
            if (token_count == 4) {
                token_count++;
                break;
            }
            tokens[token_count++] = token;
        }
        if (token_count == 0) continue;
        if (token_count > 3) {
            fprintf(stderr, "Too many arguments. Paths cannot contain spaces.\n");
            continue;
        }
        (void)dispatch(tokens, token_count, &should_exit);
    }
    free(line);
    puts("Goodbye.");
    return 0;
}
