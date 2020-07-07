import logging

import flask
from flask import current_app
from flask_socketio import emit, join_room

from application import GameManager, GAME_MANAGER_CONFIG_KEY
from .. import socketio

LOG = logging.getLogger("GameState")


@socketio.on("join")
def joined_event(message):
    room = message["room"]
    join_room(room)

    session_id = flask.request.sid
    ip_address = flask.request.remote_addr

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        LOG.info(f"User {ip_address} has joined room {room}")
        emit("valid_guesses_refresh", {"guesses": list(game_state.get_player_valid_guesses(ip_address))}, to=session_id)
    else:
        LOG.warning(f"User {ip_address} has joined invalid room {room}")


@socketio.on("guess")
def guess_word_event(message):
    session_id = flask.request.sid
    ip_address = flask.request.remote_addr
    LOG.info(f"Received guess from {ip_address}: {message}")

    room = message["room"]
    guessed_word = message["guess"]

    game_state = _get_game_manager().get_game_state(room)
    reply = game_state.guess_word(ip_address, guessed_word)

    emit("guess_reply", {"valid": reply, "guess": guessed_word}, to=session_id)


@socketio.on("new_game")
def new_game_event(message):
    LOG.debug(f"Received new_game: {message}")

    room = message["room"]
    _get_game_manager().create_game_for_name(room)

    emit("reload_page", {}, room=room)


def _get_game_manager() -> GameManager:
    return current_app.config[GAME_MANAGER_CONFIG_KEY]
