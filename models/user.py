from models import db  # Importar la instancia de db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    confirmation_code = db.Column(db.String(6), nullable=True)
    is_confirmed = db.Column(db.Boolean, default=False)
    confirmation_time = db.Column(db.DateTime, nullable=True)  # Para almacenar el tiempo de confirmación
    
def __repr__(self):
        return f'<User {self.email}>'  # Devuelve el email del usuario al imprimir el objeto
    
