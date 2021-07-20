# Documentation

This directory contains useful documentation for working with and using our TUI application.

## Installing Project Dependencies
- If you haven’t used `poetry` before but are comfortable with virtualenvs, just run `pip install poetry` in the virtualenv you’re already using and invoke the command below from the cloned repo. It will do the correct thing.
- Make sure you are in the root project directory. This directory will have a file titled `pyproject.toml`.
- Install project dependencies.

  ```bash
  $ poetry install
  $ poetry run task precommit
  ```

## Table of contents

* [Setup Guide](setup.md)

  * [API Setup](setup.md#API-Setup)
  * [Run The API](setup.md#Run-The-API)

* [Getting Started Guide](getting-started.md)

  * [Running The Game](getting-started.md#Run-The-Game)
