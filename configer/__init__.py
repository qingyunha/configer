from .configer import Configer
from .configer import C

# API
# Set the name of config file (without extension)
set_name = C.set_name

# Add config file search paths
add_path = C.add_path

# Find and read the config file
read = C.read

# Getting values from configer
get = C.get

# Working with Environment Variables
bind_env = C.bind_env
get_env = C.get_env
set_env_prefix = C.set_env_prefix

# Setting overrides
set = C.set

# Establishing defaults
set_default = C.set_default

# Watching and re-reading config files
watch_config = C.watch_config

reset = C.reset
