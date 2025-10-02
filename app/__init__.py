from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from config import Config


db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    
    db.init_app(app)
    migrate.init_app(app, db)
    app.config['SWAGGER'] ={
        'title': 'Task Manager API',
        'uiversion': 3,
        'securityDefinitions': {
            'bearerAuth': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
            }
        },
        'security': [{'bearerAuth': []}]
    }
    Swagger(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app

from app import models