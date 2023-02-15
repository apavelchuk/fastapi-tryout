from environs import Env


class ConfigFromEnv:
    def __init__(self):
        self.env = Env()
        self.env.read_env(recurse=True)

    def get(self, name, default=None):
        return self.env(name, default)


Config = ConfigFromEnv()
