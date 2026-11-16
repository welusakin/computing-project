#ifndef DATA_STRUCTURES_VISUALIZER_STRUCTURES_HPP
#define DATA_STRUCTURES_VISUALIZER_STRUCTURES_HPP

#include <algorithm>
#include <deque>
#include <memory>
#include <queue>
#include <utility>
#include <vector>

template <typename T>
class Stack {
public:
    bool empty() const noexcept { return values_.empty(); }
    std::size_t size() const noexcept { return values_.size(); }

    void push(const T &value) { values_.push_back(value); }

    bool pop(T &value) {
        if (values_.empty()) return false;
        value = values_.back();
        values_.pop_back();
        return true;
    }

    bool peek(T &value) const {
        if (values_.empty()) return false;
        value = values_.back();
        return true;
    }

    std::vector<T> top_to_bottom() const {
        return std::vector<T>(values_.rbegin(), values_.rend());
    }

private:
    std::vector<T> values_;
};

template <typename T>
class Queue {
public:
    bool empty() const noexcept { return values_.empty(); }
    std::size_t size() const noexcept { return values_.size(); }

    void enqueue(const T &value) { values_.push_back(value); }

    bool dequeue(T &value) {
        if (values_.empty()) return false;
        value = values_.front();
        values_.pop_front();
        return true;
    }

    bool peek(T &value) const {
        if (values_.empty()) return false;
        value = values_.front();
        return true;
    }

    std::vector<T> front_to_back() const {
        return std::vector<T>(values_.begin(), values_.end());
    }

private:
    std::deque<T> values_;
};

template <typename T>
class BinarySearchTree {
    struct Node {
        explicit Node(const T &value) : key(value) {}
        T key;
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;
    };

public:
    bool insert(const T &value) { return insert_at(root_, value); }
    bool contains(const T &value) const { return contains_at(root_.get(), value); }
    bool remove(const T &value) { return remove_at(root_, value); }
    bool empty() const noexcept { return !root_; }
    std::size_t size() const noexcept { return size_at(root_.get()); }
    std::size_t height() const noexcept { return height_at(root_.get()); }

    std::vector<T> inorder() const {
        std::vector<T> result;
        inorder_at(root_.get(), result);
        return result;
    }

    std::vector<T> preorder() const {
        std::vector<T> result;
        preorder_at(root_.get(), result);
        return result;
    }

    std::vector<T> postorder() const {
        std::vector<T> result;
        postorder_at(root_.get(), result);
        return result;
    }

    std::vector<T> levelorder() const {
        std::vector<T> result;
        if (!root_) return result;
        std::queue<const Node *> pending;
        pending.push(root_.get());
        while (!pending.empty()) {
            const Node *node = pending.front();
            pending.pop();
            result.push_back(node->key);
            if (node->left) pending.push(node->left.get());
            if (node->right) pending.push(node->right.get());
        }
        return result;
    }

    std::vector<std::vector<T>> levels() const {
        std::vector<std::vector<T>> result;
        if (!root_) return result;
        std::queue<const Node *> pending;
        pending.push(root_.get());
        while (!pending.empty()) {
            const std::size_t count = pending.size();
            std::vector<T> level;
            level.reserve(count);
            for (std::size_t i = 0; i < count; ++i) {
                const Node *node = pending.front();
                pending.pop();
                level.push_back(node->key);
                if (node->left) pending.push(node->left.get());
                if (node->right) pending.push(node->right.get());
            }
            result.push_back(std::move(level));
        }
        return result;
    }

private:
    std::unique_ptr<Node> root_;

    static bool insert_at(std::unique_ptr<Node> &node, const T &value) {
        if (!node) {
            node = std::make_unique<Node>(value);
            return true;
        }
        if (value == node->key) return false;
        return value < node->key
            ? insert_at(node->left, value)
            : insert_at(node->right, value);
    }

    static bool contains_at(const Node *node, const T &value) {
        if (!node) return false;
        if (value == node->key) return true;
        return value < node->key
            ? contains_at(node->left.get(), value)
            : contains_at(node->right.get(), value);
    }

    static bool remove_at(std::unique_ptr<Node> &node, const T &value) {
        if (!node) return false;
        if (value < node->key) return remove_at(node->left, value);
        if (node->key < value) return remove_at(node->right, value);
        if (!node->left) {
            node = std::move(node->right);
            return true;
        }
        if (!node->right) {
            node = std::move(node->left);
            return true;
        }
        const Node *successor = node->right.get();
        while (successor->left) successor = successor->left.get();
        const T successor_key = successor->key;
        node->key = successor_key;
        return remove_at(node->right, successor_key);
    }

    static std::size_t size_at(const Node *node) noexcept {
        return node ? 1 + size_at(node->left.get()) + size_at(node->right.get()) : 0;
    }

    static std::size_t height_at(const Node *node) noexcept {
        return node ? 1 + std::max(height_at(node->left.get()), height_at(node->right.get())) : 0;
    }

    static void inorder_at(const Node *node, std::vector<T> &result) {
        if (!node) return;
        inorder_at(node->left.get(), result);
        result.push_back(node->key);
        inorder_at(node->right.get(), result);
    }

    static void preorder_at(const Node *node, std::vector<T> &result) {
        if (!node) return;
        result.push_back(node->key);
        preorder_at(node->left.get(), result);
        preorder_at(node->right.get(), result);
    }

    static void postorder_at(const Node *node, std::vector<T> &result) {
        if (!node) return;
        postorder_at(node->left.get(), result);
        postorder_at(node->right.get(), result);
        result.push_back(node->key);
    }
};

#endif
