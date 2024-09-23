from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = "mad1.sqlite"
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SECRET_KEY'] = 'abcdefghijklmnop'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    # Login manager configuration (kept intact as requested)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'You cannot proceed without logging in'
    login_manager.init_app(app)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    with app.app_context():
        db.create_all()
        create_admin_user()

    return app

def create_admin_user():
    from .models import User, Admin
    admin_email = 'admin@gmail.com'
    admin_password = 'admin123'
    
    existing_admin = User.query.filter_by(email=admin_email).first()
    if not existing_admin:
        admin_user = User(email=admin_email, 
                          name='Admin User', 
                          password=generate_password_hash(admin_password, method='pbkdf2:sha256'),
                          role='admin')
        db.session.add(admin_user)
        db.session.commit()
        
        admin = Admin(id=admin_user.id)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")