class ConfigItem:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def toString(self):
        return "{}={}\n".format(self.key, self.value)
