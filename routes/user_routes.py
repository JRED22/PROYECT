from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User
from . import user_bp  # Importa el blueprint de el modelo User
import random
import string
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


# Initialize the Mail object
mail = Mail()


@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            if User.query.filter_by(email=email).first():
                flash('Correo Ya Existe.')
                return redirect(url_for('user.register'))

            if User.query.filter_by(username=username).first():
                flash('Usuario ya Existe .')
                return redirect(url_for('user.register'))
            confirmation_code = ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=6))
            hashed_password = generate_password_hash(
                password, method='pbkdf2:sha256')
            new_user = User(username=username, email=email, password=hashed_password,
                            confirmation_code=confirmation_code, confirmation_time=datetime.now())
            db.session.add(new_user)
            db.session.commit()
            # Enviar el código de confirmación por correo electrónico
            # Supón que aquí manejas el formulario y la creación del usuario
    # Lógica para enviar el correo aquí
            try:
                token = encode_token(email)
                # busca el metodo confirm_email -external=Truegenera una url_compleja (http o https)
                confirm_url = url_for(
                    'user.confirm_email', token=token, _external=True)
                msg = Message(subject='¡Hola desde Flask!',
                              sender='MS_nhRWXj@trial-pq3enl6om1ml2vwr.mlsender.net',
                              # Cambia esto por el destinatario
                              recipients=[email])
                # Cargar el contenido HTML desde el archiv
                msg.html = render_template(
                    'auth/email.html', code=confirmation_code, nombre_user=username, token=token, confirm_url=confirm_url)
                mail.send(msg)
                flash('Correo enviado exitosamente!')
            except Exception as e:
                flash(f'Error al enviar el correo: {e}')

            return redirect(url_for('user.login'))
        except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de error
            flash('Ocurrió un error al crear el usuario. Inténtalo de nuevo.')
            # Imprimir el error en la consola para depuración
            print(f'Error: {e}')
    return render_template('auth/register.html')


@user_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:

            user = User.query.filter_by(email=email).first()
            if not user.is_confirmed :
             flash('Por favor, confirma tu cuenta antes de iniciar sesión.')
             return redirect(url_for('user.login'))
            if not user or not check_password_hash(user.password, password):
                flash('Correo o password invalido.')
                return redirect(url_for('user.login'))
            login_user(user)
            return redirect(url_for('user.dashboard'))
        except Exception as e:
            flash('Ocurrió un error al intentar iniciar sesión. Inténtalo de nuevo.')

    return render_template('auth/login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    # flash('Logged out successfully!')
    return redirect(url_for('user.login'))


@user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

def encode_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirm-salt')

def decode_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])#seria
    try:
        email = serializer.loads(
        token, salt='email-confirm-salt', max_age=expiration)
        return email
    except Exception:
        return False
@user_bp.route('/confirm/<token>')
def confirm_email(token):
    email = decode_token(token)#llama el metodo 
    if not email:
        flash('El enlace de confirmación es inválido o ha expirado.', 'danger')
        return redirect(url_for('user.login'))
    user = User.query.filter_by(email=email).first()
    if user.is_confirmed :
        flash('La cuenta ya ha sido confirmada.', 'success')
        return redirect(url_for('user.login'))
    user.is_confirmed = True
    db.session.commit()
    flash('Has confirmado tu cuenta. ¡Gracias!', 'success')
    return redirect(url_for('user.login'))


