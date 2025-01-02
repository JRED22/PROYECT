from flask import Flask,render_template
from flask_login import  current_user
from dotenv import load_dotenv
import os
from models import db
from flask_migrate import Migrate
from models.user import User
from flask_login import LoginManager
from routes import user_bp  # Import the user blueprint

# Load environment variables
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Configure the MySQL database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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

@app.route('/')
def home():
    return render_template('home.html', user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables in the database
    app.run(debug=True)
