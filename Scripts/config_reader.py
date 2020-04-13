import configparser

class ConfigReader:

    def __init__(self):
        self.filename = 'config.ini'

    def read_default_config(self):
        self.config = configparser.ConfigParser()
        self.config.read(self.filename)
        self.configuration=self.config['DEFAULT']

        print("Config Data has read Successfully")

        return self.configuration