import os

class Config:
    
    MAIL_SERVER = 'smtp.mailersend.net'
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'  # Convertir a booleano
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL') == 'false' # Convertir a booleano
    MAIL_USERNAME = 'MS_U3yUIf@trial-pq3enl6om1ml2vwr.mlsender.net'
    MAIL_PASSWORD = '20ryhEDOk09EBe74' 
    MAIL_DEFAULT_SENDER = 'MS_U3yUIf@trial-pq3enl6om1ml2vwr.mlsender.net'
    print("MAIL_SERVER:", os.getenv('MAIL_SERVER'))
    print("MAIL_PORT:", os.getenv('MAIL_PORT'))
    print("MAIL_USERNAME:", os.getenv('MAIL_USERNAME'))
    print("MAIL_PASSWORD:", os.getenv('MAIL_PASSWORD'))
   
    
    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')