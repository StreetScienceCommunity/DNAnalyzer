from flask import Flask, render_template, request, flash
from flask_marshmallow import Marshmallow
import os
from utils import db, ma
from flask_login import LoginManager, login_required
from db_config import DB_CONFIG
from init_yaml_to_db import yaml_to_db
basedir = os.path.abspath(os.path.dirname(__file__))


def register_extensions(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@localhost/%s' % (
        DB_CONFIG['USERNAME'], DB_CONFIG['PASSWORD'], DB_CONFIG['DB_NAME'])
    db.init_app(app)
    from routes import main
    app.register_blueprint(main.bp)
    ma.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'dnapi.login'
    login_manager.init_app(app)

    from models.all_models import User
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


# Init app
def create_app():
    app = Flask(__name__)
    register_extensions(app)
    return app


app = create_app()
app.secret_key = 'Imthesercretkeyhaha'


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


# Run server
if __name__ == '__main__':
    yaml_to_db()
    app.run(debug=True)
