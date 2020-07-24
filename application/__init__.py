import logging

from flask import Flask
from flask_socketio import SocketIO

from application.data.game_manager import GameManager
from application.data.word_manager import WordManager

GAME_MANAGER_CONFIG_KEY = "game_manager"

socketio = SocketIO()

logging.basicConfig(level=logging.INFO)
logging.getLogger("engineio.server").setLevel(logging.WARNING)
logging.getLogger("socketio.server").setLevel(logging.WARNING)


def create_flask_app() -> Flask:
    # Create the flask app
    app = Flask(__name__)

    # Create a DAO and add it to the flask app config for access by the blueprints
    word_manager = WordManager()
    app.config[GAME_MANAGER_CONFIG_KEY] = GameManager(word_manager)

    from .networking import main as main_blueprint

    app.register_blueprint(main_blueprint)
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60

    socketio.init_app(app)

    return app
