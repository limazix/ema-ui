import os
import yaml

class ConfigHandler:
    _instance = None
    _configs = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigHandler, cls).__new__(cls)
        return cls._instance

    def _build_config_path(self, relative_path: str) -> str:
        """
        Builds the absolute path for a configuration file given a relative path
        from the location of this config_handler.py file.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, relative_path)

    def load_config(self, module_name, config_path):
        """
        Loads configuration from a YAML file for a specific module.

        Args:
            module_name (str): The name of the module.
            config_path (str): The path to the configuration file.
        """
        absolute_config_path = self._build_config_path(config_path)
        if not os.path.exists(absolute_config_path):
            print(f"Warning: Config file not found for module '{module_name}' at '{absolute_config_path}'")
            self._configs[module_name] = {}
            return

        with open(absolute_config_path, 'r') as f:
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
        module_config = self._configs.get(module_name, {})

        if key is None:
            return module_config
        else:
            return module_config.get(key, default)

# Example Usage (within a module's initialization)
# from app.utils.config import ConfigHandler
# config_handler = ConfigHandler()
# config_handler.load_config("my_feature", "app/my_feature/config.yaml")

# To access config within the module
# config_handler = ConfigHandler() # Get the singleton instance
# my_value = config_handler.get_config("my_feature", "some_setting")