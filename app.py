from flask import Flask

from config import Config
from routes import stream_blueprint, tuner_blueprint


def create_app(config_object: object = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.register_blueprint(tuner_blueprint)
    app.register_blueprint(stream_blueprint)
    return app


if __name__ == "__main__":
    from waitress import serve

    application = create_app()
    serve(application, host="0.0.0.0", port=5000)
