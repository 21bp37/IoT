"""Flask configuration."""


class Config:
    UPLOAD_FOLDER = 'uploads/'


class Dev(Config):
    TESTING = True
    DEBUG = True
