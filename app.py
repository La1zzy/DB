from flask import Flask
from flask_jwt_extended import JWTManager
from models import db, TokenBlocklist
from routes import routes
from config import Config
from datetime import datetime, timezone

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    if isinstance(config_class, str):
        app.config.from_object(config_class)
    else:
        app.config.from_object(config_class)
        
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # JWT configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()
        return token is not None
    
    app.register_blueprint(routes)
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
