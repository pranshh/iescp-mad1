from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Admin, Sponsor, Influencer
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
import re

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('main.dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    return render_template("login.html", user=current_user)

@auth.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, role='admin').first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in as admin successfully.', category='success')
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Invalid email or password.', category='error')
    return render_template('admin_login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        role = request.form.get('role')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif not re.search(r'[a-z]', password1):
            flash('Password must contain a lowercase character', category='error')
        elif not re.search(r'[A-Z]', password1):
            flash('Password must contain a uppercase character', category='error')
        else:
            new_user = User(email=email, name=name, password=generate_password_hash(password1, method='pbkdf2:sha256'), role=role)
            db.session.add(new_user)
            db.session.commit()

            if role == 'sponsor':
                company_name = request.form.get('company_name')
                industry = request.form.get('industry')
                budget = float(request.form.get('budget'))
                new_sponsor = Sponsor(id=new_user.id, company_name=company_name, industry=industry, budget=budget)
                db.session.add(new_sponsor)
            elif role == 'influencer':
                category = request.form.get('category')
                niche = request.form.get('niche')
                reach = int(request.form.get('reach'))
                new_influencer = Influencer(id=new_user.id, category=category, niche=niche, reach=reach)
                db.session.add(new_influencer)

            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('main.dashboard'))

    return render_template("register.html", user=current_user)