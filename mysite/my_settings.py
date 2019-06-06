import yaml

class Settings:
    __instance = None
    settings = None

    @staticmethod
    def get_settings():
        if Settings.__instance is None:
            Settings()
        return Settings.__instance.settings

    def __init__(self):
        if Settings.__instance is not None:
            raise Exception("This class is singleton!")
        else:
            with open('settings.yml', 'r') as settings_file:
                self.settings = yaml.load(settings_file, yaml.Loader)
            Settings.__instance = self