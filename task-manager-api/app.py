"""Application factory. Run locally with: flask --app app run"""
from flask import Flask, jsonify

from database import make_session
from errors import NotFoundError, ValidationError
from routes import tasks, users


def create_app(database_url: str = "sqlite:///tasks.db") -> Flask:
    app = Flask(__name__)
    session = make_session(database_url)
    app.extensions["db_session"] = session

    app.register_blueprint(tasks.bp)
    app.register_blueprint(users.bp)

    @app.errorhandler(ValidationError)
    def handle_validation(err: ValidationError):
        return jsonify({"error": "ValidationError", "message": err.message, "field": err.field}), 422

    @app.errorhandler(NotFoundError)
    def handle_not_found(err: NotFoundError):
        return jsonify({"error": "NotFoundError", "message": err.message}), 404

    @app.teardown_appcontext
    def remove_session(exc=None):
        session.remove()

    return app

