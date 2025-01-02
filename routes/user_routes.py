from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db
from models.user import User
from . import user_bp  # Importa el blueprint de el modelo User

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Correo Ya Existe.')
            return redirect(url_for('user.register'))
        
        if User.query.filter_by(username=username).first():
            flash('Usuario ya Existe .')
            return redirect(url_for('user.register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_password)

        db.session.add(new_user)
        db.session.commit()

        flash('Usuario Creado!')
        return redirect(url_for('user.login'))

    return render_template('auth/register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Correo o password invalido.')
            return redirect(url_for('user.login'))

        login_user(user)
        #flash('Logged in successfully!')
        return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')

@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    #flash('Logged out successfully!')
    return redirect(url_for('user.login'))

@user_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)
