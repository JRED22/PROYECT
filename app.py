from flask import Flask,render_template
from flask_login import  current_user
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from models import db
from flask_migrate import Migrate
from models.user import User
from flask_login import LoginManager
from routes import user_bp  # Import the user blueprint
from config import Config
from flask_mail import Mail, Message

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)# Configuracion B
mail = Mail(app)
csrf = CSRFProtect(app)
# Initialize the database and login manager
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'user.login'  # Update to use the blueprint

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register the user routes blueprint
app.register_blueprint(user_bp)

@app.route('/sendmail')
def send_email():
    # Especificar el remitente en el mensaje
    msg = Message(subject='¡Hola desde Flask!',
                  sender='MS_U3yUIf@trial-pq3enl6om1ml2vwr.mlsender.net',  # Especifica el remitente aquí
                  recipients=['alt.h4-boa6mi0e@yopmail.com'])  # Especifica el destinatario aquíS
    msg.body = "Este es un correo de prueba enviado desde una aplicación Flask."

    try:
        mail.send(msg)
        return 'Correo enviado!'
    except Exception as e:
        return f'Error al enviar el correo: {e}'

      
@app.route('/')
def home():
    return render_template('home.html', user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables in the database
    app.run(debug=True)
