import logging
import random
import string
from typing import List, Dict

from application.data.game_tile import GameTile
from application.data.game_update import GameUpdate
from application.data.word_manager import WordManager

TOTAL_TILES = 25

LOG = logging.getLogger("GameState")


class GameState:
    """
    Class representing the state of a game.
    """

    def __init__(self, game_name: str, word_manager: WordManager):
        """
        Generates a new, random game state.
        """
        self.game_name = game_name
        self.word_manager = word_manager
        self.game_tiles = GameState._generate_tiles()

        self._log_info("Created new game")

    def guess_word(self, player_id: str, guessed_word: str) -> bool:
        """
        Updates the game state to reflect the guessed word.
        If the guess is not correct, the current team's turn is ended.
        Returns the GameUpdate to send to clients.

        Args:
            player_id: The player
            guessed_word: The guessed word

        Returns:
            whether the guess was successful
        """
        self._log_info(f"{player_id} has guessed word {guessed_word}")

        if not self.word_manager.is_word(guessed_word):
            self._log_info(f"{player_id} guess word {guessed_word} is not a valid word")
            return False

    def _word_is_on_board(self, guessed_word: str) -> bool:
        possible_paths = []

        for i in range(0, len(self.game_tiles)):
            if self.game_tiles[i] == guessed_word[0]:
                possible_paths.append(i)

        for character in guessed_word[1:]:
            for i in range(0, len(self.game_tiles)):
                if self.game_tiles[i] == character:
                    pass  # TODO algorithm

    def _log_info(self, log_message: str):
        LOG.info("[%s] %s", self.game_name, log_message)

    @staticmethod
    def _tiles_are_neighbors(tile_index_1: int, tile_index_2: int) -> bool:
        # Calculate the relationship between the two tiles for easier calculation
        smaller_tile = min(tile_index_1, tile_index_2)
        larger_tile = max(tile_index_1, tile_index_2)

        # Ensure we don't go out of bounds
        if (smaller_tile < 0) or (larger_tile >= TOTAL_TILES):
            raise ValueError("Tile indexes invalid")

        difference = larger_tile - smaller_tile

        if larger_tile % 5 == 0:
            # Tiles on the left-most column
            return difference in [4, 5]
        elif (larger_tile + 1) % 5 == 0:
            # Tiles on the right-most column
            return difference in [1, 5, 6]
        else:
            # All other tiles
            return difference in [1, 4, 5, 6]

    @staticmethod
    def _generate_tiles() -> List[str]:
        tiles = []
        for i in range(0, 25):
            tiles[i] = random.choice(string.ascii_lowercase)
        return tiles
