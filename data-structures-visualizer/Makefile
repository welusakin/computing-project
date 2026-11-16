CXX ?= c++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Wpedantic -O2

.PHONY: all clean

all: data-structures-visualizer

data-structures-visualizer: src/main.cpp include/structures.hpp
	$(CXX) $(CXXFLAGS) -Iinclude -o $@ src/main.cpp

clean:
	rm -f data-structures-visualizer
