from flask import make_response, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
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
        try:
         new_user = User(username=username, email=email, confirmation_code=confirmation_code, confirmation_time=datetime.now())
         new_user.set_password(password)  # Aquí se codifica la contraseña
        except Exception as e:
             flash(f'Error al crear el usuario Verificalo: {e}', 'danger')  
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
            flash('Registro Exitoso! Se ha enviado un correo de confirmación.', 'success')
            return redirect(url_for('user.login'))
        except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de error
            flash(f'Error al enviar Correo: {e}', 'danger')

    return render_template('auth/registro.html', form=form)

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  
    try:
     if form.password.data !='' and form.email.data !='':     
      if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user.check_password(form.password.data):
          login_user(user)
          return redirect(url_for('user.dashboard'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'danger')  
     else:
          flash('')
          
          
    except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de error
            flash(f'Error al validar el usuario: {e}', 'danger')  
    return render_template('auth/login.html', form=form)

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()  # Cierra la sesión del usuario
    response = make_response(redirect(url_for('user.login')))  # Redirige a la página de inicio de sesión
    response.headers['Cache-Control'] = 'no-store'  # Evita que la página se almacene en caché
    response.headers['Pragma'] = 'no-cache'  # Evita que la página se almacene en caché
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.must_revalidate = True
    response.expires = 0
    return response


@user_bp.route('/dashboard')
@login_required
def dashboard():
    print(f'Usuario autenticado: {current_user.is_authenticated}')  # Para depuración
    return render_template('dashboard.html', user=current_user)

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
    try:
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
    except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de error
            flash(f'Error crear vinculo de confirmacion: {e}', 'danger')
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
                flash('Se ha enviado un correo para restablecer la contraseña.', 'success')
            except Exception as e:
                flash(f'Error al enviar el correoc de reset password: {e}')
                return redirect(url_for('user.login'))
        else:
            
         flash('No existe un usuario con ese correo electrónico.', 'danger')
    
    return render_template('auth/reset_password_request.html', form=form)

@user_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = ResetPasswordForm()
    if form.password.data !='':
        if form.validate_on_submit():
          if form.password.data != form.confirm_password.data:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('user.reset_password', token=token))
          try:   
            # Aquí deberías incluir la lógica para actualizar la contraseña del usuario
            email = decode_token(token)  # Asegúrate de tener un método para verificar el token
            user = User.query.filter_by(email=email).first()
            if user:
                user.set_password(form.password.data)
                db.session.commit()
                flash('Tu contraseña ha sido restablecida con éxito.', 'success')
                return redirect(url_for('user.login'))
            else:
                flash('El token es inválido o ha expirado.', 'danger')
                return redirect(url_for('user.login'))
          except Exception as e:
            db.session.rollback()  # Deshacer la sesión en caso de error
            flash(f'Error al actualizar Contraseña: {e}', 'danger')
    else:
        flash('')       
    return render_template('auth/reset_password.html', form=form)