#Grösstenteils aus Emanuel Grimbergs Blog übernommen
import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Leider nicht richtig'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:3x&J)PM1q!Ew@localhost:3306/ReptXpert'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = os.environ.get('MAIL_Server')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['l.l.m@gmx.ch']
    POSTS_PER_PAGE = 25
    