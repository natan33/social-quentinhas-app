import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager
from flask_migrate import Migrate # Importe Migrate aqui

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

# Inicialize db e login_manager globalmente, mas sem o app ainda
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# A variável 'app' será definida globalmente aqui após a criação pela fábrica,
# para que possa ser importada por outros módulos como routes.py
app = None
global migrate # Inicialize migrate como None também

def create_app():
    global app, migrate # Declare que você vai modificar as variáveis globais 'app' e 'migrate'
    
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-testing")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configure the database
    database_url = os.environ.get("DATABASE_URL", "sqlite:///vendas_quentinhas.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Initialize extensions with the app instance
    db.init_app(app)
    login_manager.init_app(app)

    # Inicialize o Flask-Migrate aqui, após 'app' e 'db' estarem definidos e inicializados
    migrate = Migrate(app, db) 

    login_manager.login_view = 'login'  # Rota de login

    with app.app_context():
        # Import models and routes AFTER 'app' and 'db' are initialized
        # This ensures they have access to the fully configured 'app' and 'db'
        import models
        import routes 
        
        # Crie todas as tabelas. Com Flask-Migrate, você normalmente usa 'flask db upgrade'.
        # Mantenha esta linha apenas para a primeira vez que você roda o app em desenvolvimento,
        # ou se não for usar migrações.
        # db.create_all()
        pass 

        @app.errorhandler(403)
        def erro_403(e):
            return render_template('403.html'), 403
        
    return app