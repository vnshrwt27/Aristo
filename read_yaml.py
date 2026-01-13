import yaml
file_path= "/home/itzfranku/Aristo/test.yaml"
with open(file_path, "r") as yaml_file:
    x=yaml.safe_load(yaml_file)
print(x)
print(x.get("test").get("name"))
