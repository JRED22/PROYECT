from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User  # Import the User model

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Este campo es obligatorio.'),Length(min=3, max=25, message='El nombre de usuario debe tener entre 3 y 25 caracteres.')])
    email = StringField('Email', validators=[DataRequired(message='Email es Requerido.'), Email('Ingrese una direccion de Correo.')])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir.')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
     user = User.query.filter_by(username=username.data).first()
     if user:
      raise ValidationError('Usuario existente.')
 
    def validate_email(self, email):
        # Validación personalizada para verificar si el email ya está en uso
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email ya está en uso. Por favor, elige otro.')

    def validate_password(self, password):
        # Validación personalizada para verificar la fortaleza de la contraseña
        if len(password.data) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not any(char.isalpha() for char in password.data):
            raise ValidationError('La contraseña debe contener al menos una letra.')

