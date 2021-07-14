import logging
import os
import platform
import time
from typing import Optional, Union

import yaml
from blessed import Terminal

from app.configuration.validators.run_validations import fix_config
from app.constants import Configuration

log = logging.getLogger(__name__)


class ConfigLoader:
    """Loads yaml config files to customize piston-cli."""

    def __init__(self, paths: Optional[Union[str, tuple]] = None):
        if paths:
            self.paths = paths
        elif platform.system() in Configuration.configuration_paths:
            self.paths = Configuration.configuration_paths[platform.system()]
        self.config = {}

        self.path_loaded = None

    def _load_yaml(self, term: Terminal) -> None:
        """Loads the keys and values from a yaml file."""
        expanded_path = os.path.abspath(os.path.expandvars(self.path_loaded))

        print(term.blue(f"\nLoading config: {expanded_path}"))

        with open(expanded_path) as loaded_config:
            loaded_config = yaml.load(loaded_config, Loader=yaml.FullLoader)

        for key, value in loaded_config.items():
            if key in Configuration.tokens:
                self.config[key] = value
                print(term.blue(f"Loaded {key}(s): {value}"))

    def load_config(self, term: Terminal) -> Optional[dict]:
        """Loads the configuration file."""
        existing_paths = []

        if isinstance(self.paths, str):
            if os.path.isfile(self.paths):
                existing_paths.append(self.paths)
        elif isinstance(self.paths, tuple):
            for path in self.paths:
                if os.path.isfile(path):
                    existing_paths.append(path)

        if len(existing_paths) > 1:
            print(
                term.blue(
                    "One or more configuration files were found to exist. "
                    f"Using the one found at {existing_paths[0]}."
                )
            )

        if (
            not existing_paths
            # The path is not in a default location,
            # this means that it is None from an unrecognized system or was manually specified
            and self.paths not in Configuration.configuration_paths.values()
        ):
            print(
                term.red(
                    "No configuration file found at that location or "
                    "you are using a system with an unknown default configuration file location"
                )
            )
            return False

        elif (
            # The path is in a default location, a path was probably not specified,
            # unless the user pointed to one in the default location
            not existing_paths
            and self.paths in Configuration.configuration_paths.values()
        ):
            term.red(("No default configuration file found on your system"))
            return False

        # Choose the first path which is loaded
        self.path_loaded = existing_paths[0]
        self._load_yaml(term)  # Set config
        return self.config

    def config_loader_screen(self, term: Terminal) -> Optional[bool]:
        """Screen showing the erros and configuration loaded by the module."""
        print(term.home + term.clear + term.move_y(0))
        print(term.bold_black_on_green(term.center("Loading Configurations")))
        print("\n")

        config = self.load_config(term)
        if not config:
            self.exit(term)
            return False

        # Configuration validator
        response = fix_config(config, term)
        if not response:
            self.exit(term)
            return False

        time.sleep(10)

    @staticmethod
    def exit(term: Terminal) -> None:
        """Show the invalid configuration exit screen."""
        print("\n\n")
        print(
            term.bold_white_on_red(
                term.center("Error loading the configuration. Exiting in 10 seconds...")
            )
        )
        time.sleep(10)
        print(term.clear + term.exit_fullscreen + term.clear)
