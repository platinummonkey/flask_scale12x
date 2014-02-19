from base import BaseConfig

class Development(BaseConfig):
    HOST = '127.0.0.1'
    PORT = 8000

class DevelopmentCI(Development):
    HOST = '0.0.0.0'
    PORT = 8080
