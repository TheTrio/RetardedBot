# RetardedBot

A silly Discord Bot I made

## Setup

[pipenv](https://github.com/pypa/pipenv) is used for managing the dependencies, [autopep8](https://github.com/hhatto/autopep8) for the formatting, [flake8](https://github.com/PyCQA/flake8) for linting and [pytest](https://github.com/pytest-dev/pytest) for testing.

### Install

`pipenv install` for installing the dependencies and then `pipenv shell` for entering the virtual environment.
### Linting
```
flake8 . --count --max-line-length=127
```
### Testing
The config for `pytest` is stored in `pytest.ini`. Simply run `pytest` from within the virtual environment
