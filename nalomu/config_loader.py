from os import path
import toml

from nalomu import NDict

path_conf = f'{path.dirname(path.realpath(__file__))}/conf'


class ConfLoader:
    file = f'{path_conf}/config.toml'
    configs = None

    def __init__(self):
        self.configs = self.toml_load()

    # @staticmethod
    def toml_load(self):
        with open(self.file, encoding="utf-8") as f:
            return NDict(**toml.load(f))

    # @staticmethod
    def toml_dump(self):
        with open(self.file, 'w', encoding="utf-8") as f:
            toml.dump(self.configs, f)

    def __getitem__(self, item):
        return self.configs[item] if item in self.configs else None

    def __getattr__(self, item):
        if item in ConfLoader.__dict__:
            return super().__setattr__(item)
        return self.__getitem__(item)

    def __setitem__(self, key, value):
        self.configs[key] = value
        self.toml_dump()

    def __setattr__(self, key, value):
        if key in ConfLoader.__dict__:
            super().__setattr__(key, value)
            return
        self.__setitem__(key, value)

    def __delattr__(self, item):
        self.__delitem__(item)
        self.toml_dump()

    def __delitem__(self, item):
        del self.configs[item]
        self.toml_dump()


config = ConfLoader()

if __name__ == '__main__':
    pass
