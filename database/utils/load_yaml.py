import yaml


def load_yaml(filename: str) -> dict:
    with open(filename, 'r') as yaml_file:
        return yaml.safe_load(yaml_file)
