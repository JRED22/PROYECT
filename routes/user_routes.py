from flask import render_template, redirect, url_for, request, flash
from wtforms.validators import ValidationError
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import db
from models.user import User
from . import user_bp  # Importa el blueprint de el modelo User
import random
import string
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from forms import RegistrationForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm

# Initialize the Mail object
mail = Mail()

@user_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.username.data
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash('El correo electrónico o el nombre de usuario ya están en uso.', 'danger')
            return redirect(url_for('user.registro'))

        confirmation_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password, confirmation_code=confirmation_code, confirmation_time=datetime.now())
        
        try:
            db.session.add(new_user)
            db.session.commit()
            token = encode_token(email)
            confirm_url = url_for('user.confirm_email', token=token, _external=True)
            msg = Message(subject='¡Hola desde Flask!',
                          sender='tu_email@ejemplo.com',  # Cambia esto por tu dirección de correo
                          recipients=[email])
            msg.html = render_template('auth/email.html', code=confirmation_code, nombre_user=username, token=token, confirm_url=confirm_url)
            mail.send(msg)
            flash('Registro Exitoso! Se ha enviado un correo de confirmación.')
            return redirect(url_for('user.login'))
        except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de error
            flash(f'Error al crear el usuario: {e}', 'danger')
    
    return render_template('auth/registro.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):  # Asegúrate de tener un método check_password
            login_user(user)
            return redirect(url_for('user.dashboard'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'danger')
    
    return render_template('auth/login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))

@user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template ('dashboard.html', user=current_user)

def encode_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')

def decode_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirm-salt', max_age=expiration)
        return email
    except Exception:
        return False

@user_bp.route('/confirm/<token>')
def confirm_email(token):
    email = decode_token(token)
    if not email:
        flash('El enlace de confirmación es inválido o ha expirado.', 'danger')
        return redirect(url_for('user.login'))
    
    user = User.query.filter_by(email=email).first()
    if user:
        if user.is_confirmed:
            flash('La cuenta ya ha sido confirmada.', 'success')
        else:
            user.is_confirmed = True
            db.session.commit()
            flash('Has confirmado tu cuenta. ¡Gracias!', 'success')
    else:
        flash('No se encontró el usuario.', 'danger')
    
    return redirect(url_for('user.login'))

@user_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                token = encode_token(email)
                confirm_url = url_for('user.reset_password', token=token, _external=True)
                msg = Message(subject='¡Hola desde Jrojo Flask!',
                              sender='tu_email@ejemplo.com',  # Cambia esto por tu dirección de correo
                              recipients=[email])
                msg.html = render_template('auth/email.html', token=token, confirm_url=confirm_url)
                mail.send(msg)
                flash('Se ha enviado un correo para restablecer la contraseña.')
            except Exception as e:
                flash(f'Error al enviar el correo: {e}')
                return redirect(url_for('user.login'))
        else:
            flash('No existe un usuario con ese correo electrónico.')
    
    return render_template('auth/reset_password_request.html', form=form)

@user_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = decode_token(token)
    if email is None:
        flash('El enlace de restablecimiento de contraseña es inválido o ha expirado.', 'danger')
        return redirect(url_for('user.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(form.password.data)  # Asegúrate de tener un método para establecer la contraseña
            db.session.commit()
            flash('Tu contraseña ha sido restablecida con éxito.')
            return redirect(url_for('user.login'))

    return render_template('auth/reset_password.html', form=form)