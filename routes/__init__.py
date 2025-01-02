from flask import Blueprint

# Create a blueprint for user routes
user_bp = Blueprint('user', __name__)

from .user_routes import *  # Import all routes from user_routes
