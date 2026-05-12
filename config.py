


class Config:
   
    SQLALCHEMY_DATABASE_URI = 'sqlite:///tmp/kasir_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "dev-secret-key"
    DEBUG = True


config = {
    'default': Config
}

