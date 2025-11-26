from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Profile
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

os.makedirs(app.instance_path, exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            login_user(user)
            return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            return "Логин уже занят", 400
        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/menu')
@login_required
def menu():
    profiles = Profile.query.filter_by(user_id=current_user.id).all()
    return render_template('menu.html', profiles=profiles)

@app.route('/add', methods=['POST'])
@login_required
def add_profile():
    p = Profile(
        user_id=current_user.id,
        full_name=request.form.get('full_name'),
        email=request.form.get('email'),
        phone=request.form.get('phone'),
        comment=request.form.get('comment')
    )
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('menu'))

@app.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit_profile(id):
    p = Profile.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    p.full_name = request.form.get('full_name')
    p.email = request.form.get('email')
    p.phone = request.form.get('phone')
    p.comment = request.form.get('comment')
    db.session.commit()
    return redirect(url_for('menu'))

@app.route('/delete/<int:id>')
@login_required
def delete_profile(id):
    p = Profile.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for('menu'))

from flask_login import logout_user

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='danil').first():
            admin = User(username='danil', password_hash=generate_password_hash('123'))
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)