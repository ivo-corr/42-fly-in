.PHONY: install run debug clean fclean lint lint-strict

PYTHON = python3
MAIN = fly_in.py
VENV_NAME = .venv

cvenv:
	$(PYTHON) -m venv $(VENV_NAME)

install: cvenv
	. $(VENV_NAME)/bin/activate && \
	$(PYTHON) -m pip install build && \
	$(PYTHON) -m build && \
	mv dist/* . && \
	rmdir dist && \
	$(PYTHON) -m pip install .

run:
	$(PYTHON) $(MAIN)

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf output.txt

# used if u want to remove venv
fclean: clean
	rm -rf build
	rm -rf *.egg-info
	rm -rf dist
	rm -rf $(VENV_NAME)
	rm -rf *.tar.gz
	rm -rf *.whl

lint:
	flake8 . --exclude=.venv,venv
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 . --exclude=.venv,venv
	mypy . --strict

# python3 -m venv .venv
# source .venv/bin/activate
# make install
# make run
# make clean
# deactivate
# make fclean