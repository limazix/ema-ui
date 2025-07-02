import os
import yaml
import json

class ConfigHandler:
    _instance = None
    _configs = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigHandler, cls).__new__(cls)
        return cls._instance

    def load_config(self, module_name, config_path):
        """
        Loads configuration from a YAML file for a specific module.

        Args:
            module_name (str): The name of the module.
            config_path (str): The path to the configuration file.
        """
        # Normalize the config_path to an absolute path
        config_path = os.path.abspath(config_path)

        if not os.path.exists(config_path):
            print(f"Warning: Config file not found for module '{module_name}' at '{config_path}'")
            self._configs[module_name] = {}
            return

        with open(config_path, 'r') as f:
            try:
                config_data = yaml.safe_load(f)
                self._configs[module_name] = config_data if config_data is not None else {}
            except yaml.YAMLError as e:
                print(f"Error loading config file for module '{module_name}' at '{config_path}': {e}")
                self._configs[module_name] = {}


    def get_config(self, module_name, key=None, default=None):
        """
        Retrieves a configuration value for a specific module.

        Args:
            module_name (str): The name of the module.
            key (str, optional): The specific configuration key to retrieve. If None, returns the entire config for the module. Defaults to None.
            default: The default value to return if the key is not found. Defaults to None.

        Returns:
            The configuration value or the default value if the key is not found.
        """
        module_config: dict = self._configs.get(module_name, {})

        if key is None:
            return module_config
        else:
            return module_config.get(key, default)
