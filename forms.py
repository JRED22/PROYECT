import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models.user import User  # Import the User model
from werkzeug.security import check_password_hash  

################################VALIDACION REGISTRO #################################################################
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message='Este campo es obligatorio.'),Length(min=3, max=40, message='El nombre de usuario debe tener entre 3 y 25 caracteres.')]
                           ,render_kw={"class": "form-control form-control-sm username","placeholder": " "})
    email = EmailField('Email', validators=[DataRequired(message='Email es Requerido.'), Email('Ingrese una direccion de Correo.')]
                        ,render_kw={"class": "form-control form-control-sm email","placeholder": " "})
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=20)]
                       ,render_kw={"class": "form-control form-control-sm password","placeholder": " "})
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir.')]
                                     ,render_kw={"class": "form-control form-control-sm password","placeholder": " "})
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
     user = User.query.filter_by(username=username.data).first()
     if user:
      raise ValidationError('Usuario existente.')
 
    def validate_email(self, email):
        # Validación personalizada para verificar si el email ya está en uso
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email  en uso. Digita otro.')

    def validate_password(self, password):
        # Validación personalizada para verificar la fortaleza de la contraseña
        if len(password.data) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not any(char.isalpha() for char in password.data):
            raise ValidationError('La contraseña debe contener al menos una letra.')
        
################################Validacion del formulario Login #################################################################
class LoginForm(FlaskForm):
      email = EmailField('Email',validators=[DataRequired(message='Correo is required.'),
                               Length(min=3, max=50, message='Email Requerido')
                               ,Email(message='Por favor, ingrese un correo electrónico válido.'),],
                           render_kw={"class": "form-control form-control-sm email", "placeholder": "Digite su Email"})
      password = PasswordField('Password',validators=[DataRequired(message='Password is required.'),
                                 Length(min=6, max=100, message='Password must be at least 6 characters long.')],
                                 render_kw={"class": "form-control", "placeholder": "Enter your password"})
      submit = SubmitField('Login',render_kw={"class": "btn btn-primary"})
      def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if not user:
            raise ValidationError('No existe un usuario con este correo electrónico.')
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'      
        if not re.match(email_regex, email):
            raise ValidationError('Caracteres Invalidos.')
        if user:
           if not user.is_confirmed:
              raise ValidationError('Por favor confirma tu correo electrónico.')
           
###############################################RESET###################################################################
class ResetPasswordRequestForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired(message='Correo is required.'),
                               Length(min=3, max=50, message='Email Requerido')
                               ,Email(message='Por favor, ingrese un correo electrónico válido.'),],
                           render_kw={"class": "form-control form-control-sm email", "placeholder": "Digite su Email"})
    submit = SubmitField('Enviar Correo')
    
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6, max=20)]
                       ,render_kw={"class": "form-control form-control-sm password","placeholder": " "})
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir.')]
                                     ,render_kw={"class": "form-control form-control-sm password","placeholder": " "})
    submit = SubmitField('Restablecer ')
    def validate_password(self, password):
        # Validación personalizada para verificar la fortaleza de la contraseña
        if len(password.data) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres.')
        if not any(char.isdigit() for char in password.data):
            raise ValidationError('La contraseña debe contener al menos un número.')
        if not any(char.isalpha() for char in password.data):
            raise ValidationError('La contraseña debe contener al menos una letra.')