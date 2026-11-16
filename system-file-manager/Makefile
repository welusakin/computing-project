CC ?= cc
CFLAGS ?= -std=c11 -Wall -Wextra -Wpedantic -O2
CPPFLAGS ?= -D_POSIX_C_SOURCE=200809L

.PHONY: all clean

all: file-manager

file-manager: src/file_manager.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ $<

clean:
	rm -f file-manager
