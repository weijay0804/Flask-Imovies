import os
from dotenv import load_dotenv

'''app 組態設定'''

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__)) #取得工作目錄

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aaaa'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    IMOVIES_ADMIN =  os.environ.get('IMOVIES_ADMIN')
    IMOVIES_SUBJECT_PERFIX = '[Imovies]'
    IMOVIES_MAIL_SENDER = 'Imoives Admin'
    IMOVIES_MOVIES_PER_PAGE = 20
    SQLALCHEMY_RECORD_QUERIES = True
    IMOVIES_SLOW_DB_QUERY_TIME = 0.5
    SSL_REDIRECT = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite://'

class ProductionConfig(Config):
    if os.environ.get('DATABASE_URL'):
        database_url = os.environ.get('DATABASE_URL').replace('postgres', 'postgresql')
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')


    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import logging
        from logging.handlers import SMTPHandler
        credits = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost = (cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr = cls.IMOVIES_MAIL_SENDER,
            toaddrs = [cls.IMOVIES_ADMIN],
            subject= cls.IMOVIES_SUBJECT_PERFIX + 'Application Error',
            credentials = credentials,
            secure = secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

class HerokuConfig(ProductionConfig):
    SSL_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)



config = {
    'development' : DevelopmentConfig,
    'testing' : TestingConfig,
    'production' :ProductionConfig,
    'heroku' : HerokuConfig,
    'default' : DevelopmentConfig
}