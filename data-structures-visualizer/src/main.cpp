#include "structures.hpp"

#include <iostream>
#include <sstream>
#include <string>

using Value = int;

template <typename T>
void print_sequence(const std::vector<T> &values, const char *empty_label) {
    if (values.empty()) {
        std::cout << empty_label;
        return;
    }
    for (std::size_t i = 0; i < values.size(); ++i) {
        if (i != 0) std::cout << " -> ";
        std::cout << values[i];
    }
}

void print_state(const Stack<Value> &stack, const Queue<Value> &queue,
                 const BinarySearchTree<Value> &tree) {
    std::cout << "\nCurrent state\n  Stack top -> ";
    print_sequence(stack.top_to_bottom(), "(empty)");
    std::cout << "\n  Queue front -> ";
    print_sequence(queue.front_to_back(), "(empty)");
    std::cout << "\n  Tree inorder -> ";
    print_sequence(tree.inorder(), "(empty)");
    std::cout << "\n  Tree size: " << tree.size() << "  height: " << tree.height() << "\n";
}

bool read_integer(const std::string &line, Value &value) {
    std::istringstream input(line);
    char extra;
    return (input >> value) && !(input >> extra);
}

void print_menu() {
    std::cout << "\nChoose an operation:\n"
              << "  1  Push onto stack\n"
              << "  2  Pop from stack\n"
              << "  3  Enqueue into queue\n"
              << "  4  Dequeue from queue\n"
              << "  5  Insert into binary search tree\n"
              << "  6  Remove from binary search tree\n"
              << "  7  Search binary search tree\n"
              << "  8  Show tree traversals by level\n"
              << "  0  Exit\n"
              << "> ";
}

int main() {
    Stack<Value> stack;
    Queue<Value> queue;
    BinarySearchTree<Value> tree;
    std::string line;
    std::cout << "Data Structures Visualizer — stack, queue, and binary search tree\n";

    while (true) {
        print_menu();
        if (!std::getline(std::cin, line)) break;
        int choice = -1;
        if (!read_integer(line, choice)) {
            std::cout << "Enter one menu number.\n";
            continue;
        }
        if (choice == 0) break;

        Value value{};
        switch (choice) {
        case 1:
        case 3:
        case 5:
            std::cout << "Integer value: ";
            if (!std::getline(std::cin, line) || !read_integer(line, value)) {
                std::cout << "Invalid integer; no change made.\n";
                break;
            }
            if (choice == 1) {
                stack.push(value);
                std::cout << "Pushed " << value << " onto the stack.\n";
            } else if (choice == 3) {
                queue.enqueue(value);
                std::cout << "Enqueued " << value << " at the back.\n";
            } else if (tree.insert(value)) {
                std::cout << "Inserted " << value << " into the tree.\n";
            } else {
                std::cout << value << " is already in the tree; duplicates are skipped.\n";
            }
            break;
        case 2:
            if (stack.pop(value)) std::cout << "Popped " << value << " from the stack.\n";
            else std::cout << "Stack is empty; nothing to pop.\n";
            break;
        case 4:
            if (queue.dequeue(value)) std::cout << "Dequeued " << value << " from the front.\n";
            else std::cout << "Queue is empty; nothing to dequeue.\n";
            break;
        case 6:
        case 7:
            std::cout << "Integer value: ";
            if (!std::getline(std::cin, line) || !read_integer(line, value)) {
                std::cout << "Invalid integer; no change made.\n";
                break;
            }
            if (choice == 6) {
                std::cout << (tree.remove(value) ? "Removed " : "Value not found: ") << value << ".\n";
            } else {
                std::cout << (tree.contains(value) ? "Found " : "Not found: ") << value << ".\n";
            }
            break;
        case 8:
            std::cout << "  Inorder:    "; print_sequence(tree.inorder(), "(empty)"); std::cout << "\n";
            std::cout << "  Preorder:   "; print_sequence(tree.preorder(), "(empty)"); std::cout << "\n";
            std::cout << "  Postorder:  "; print_sequence(tree.postorder(), "(empty)"); std::cout << "\n";
            std::cout << "  Level order: "; print_sequence(tree.levelorder(), "(empty)"); std::cout << "\n";
            for (const auto &level : tree.levels()) {
                std::cout << "    level: ";
                print_sequence(level, "(empty)");
                std::cout << "\n";
            }
            break;
        default:
            std::cout << "Unknown menu choice.\n";
            break;
        }
        print_state(stack, queue, tree);
    }
    std::cout << "Goodbye.\n";
    return 0;
}
