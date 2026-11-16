# Data Structures Visualizer

A C++17 console application for stepping through stack, queue, and binary search tree operations. Each command reports its result and prints the structures' current contents so insertions, removals, and traversal order are visible immediately.

## Structures and operations

### Stack (LIFO)

- Push an integer onto the top
- Pop the most recently pushed integer
- Display the stack from top to bottom
- Peek at the top without removing it

### Queue (FIFO)

- Enqueue an integer at the back
- Dequeue the oldest integer at the front
- Display the queue from front to back
- Peek at the front without removing it

### Binary search tree

- Insert unique integer keys
- Search for a key
- Remove a key, handling leaf, one-child, and two-child cases
- Traverse in-order, pre-order, post-order, and level-order
- Display the tree sideways, plus its size and height

## Build and run

Requires a C++17 compiler and `make`:

```bash
make
./data-structures-visualizer
```

Select a numbered operation and enter an integer when prompted. The program prints a step-by-step snapshot of the stack, queue, and tree after each mutation. `make clean` removes the executable.

## Implementation map

- `include/structures.hpp` defines reusable, templated `Stack`, `Queue`, and `BinarySearchTree` classes.
- `src/main.cpp` provides the interactive menu, safe input parsing, operation feedback, traversals, and state display.
- `Makefile` builds with warnings enabled.

The tree owns its nodes with `std::unique_ptr`; it does not leak memory when nodes are removed or when the program exits. Empty pop/dequeue operations and missing tree keys are handled without undefined behavior.

This is an independently rebuilt version based on the project scope in my notes. The original class submission files were not available.
