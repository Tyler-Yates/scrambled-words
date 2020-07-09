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
    player_id = _get_player_id()

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        LOG.info(f"User {player_id} has joined room {room}")
        # Only send the game_state update to the SocketIO session ID as the other players do not need to know
        emit("game_state", game_state.get_game_state(player_id=player_id), to=session_id)
    else:
        LOG.warning(f"User {player_id} has joined invalid room {room}")


@socketio.on("guess")
def guess_word_event(message):
    session_id = flask.request.sid
    player_id = _get_player_id()
    LOG.info(f"Received guess from {player_id}: {message}")

    room = message["room"]
    guessed_word = message["guess"]

    game_state = _get_game_manager().get_game_state(room)
    reply = game_state.guess_word(player_id, guessed_word)

    emit("guess_reply", {"valid": reply, "guess": guessed_word}, to=session_id)


@socketio.on("new_game")
def new_game_event(message):
    LOG.debug(f"Received new_game: {message}")

    room = message["room"]

    game_state = _get_game_manager().get_game_state(room)
    if game_state:
        game_state.new_board()
    else:
        game_state = _get_game_manager().create_game_for_name(room)

    emit("game_state", game_state.get_game_state(), room=room)


def _get_player_id() -> str:
    return flask.request.remote_addr


def _get_game_manager() -> GameManager:
    return current_app.config[GAME_MANAGER_CONFIG_KEY]
