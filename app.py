from flask import Flask,render_template,url_for,flash,redirect
from flask_login import  current_user
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from models import db
from flask_migrate import Migrate
from models.user import User
from flask_login import LoginManager
from routes import user_bp  # Import the user blueprint
from config import Config
from flask_mail import Mail
from flask import current_app

# Initialize the Flask application
app = Flask(__name__)
app.config.from_object(Config)# Configuracion B
mail = Mail(app)
csrf = CSRFProtect(app)
# Initialize the database and login manager
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user.login'  # Redirige a la vista de login si no está autenticado
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #desactiva archivos estaticos para no almacenar kche
@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.expires = 0
    return response
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register the user routes blueprint
app.register_blueprint(user_bp)


def get_current_user():
    return current_user if current_user.is_authenticated else None

@app.route('/')
def home():
    user = get_current_user()  # Función que obtiene el usuario actual
    return render_template('home.html',user=user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables in the database
    app.run(debug=True)
