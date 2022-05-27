# your-repo-name
This is a template repository for Oxeo.

It has some default directories and pip setup to get you started.

## How to use it
1. Customise this README (i.e. delete this section).
2. Delete any directories that you don't need.
3. Rename the directory inside `oxeo/` to your submodule name.
4. Don't put an `__init__.py` file inside `oxeo/` or you'll break things.
5. Edit `setup.cfg` lines 7-8 to reflect the name. Also add requirements to line 13 and below. Add an entrypoint if needed.
6. Or if you don't need to `pip install` this repo, comment out those lines and just edit `requirements.txt` as needed.

## Installation
```
pip install .
```

## Development
```
pip install -e .[dev]
pre-commit install
```

Run tests:
```
tox
```
