import config


def get_available_channels():
    return [loc.name for loc in config.RESULTS_PATH.iterdir() if loc.is_dir()]


def get_available_models(channel_name):
    channel_path = config.RESULTS_PATH / channel_name
    return [loc.name for loc in channel_path.iterdir() if loc.is_dir()]
