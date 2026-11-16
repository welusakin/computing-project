.PHONY: build verify clean

build:
	$(MAKE) -C system-file-manager
	$(MAKE) -C data-structures-visualizer

verify: build
	cd task-manager-api && python3 -m pytest -q
	cd pacman-search-agents && python3 -m unittest discover -s tests -v
	cd pacman-search-agents && python3 -m pacman_search --compare --goal food
	printf 'help\nexit\n' | system-file-manager/file-manager
	printf '1\n7\n3\n9\n5\n8\n8\n0\n' | data-structures-visualizer/data-structures-visualizer

clean:
	$(MAKE) -C system-file-manager clean
	$(MAKE) -C data-structures-visualizer clean
	rm -rf pacman-search-agents/pacman_search/__pycache__ pacman-search-agents/tests/__pycache__
