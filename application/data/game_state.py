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

    def __init__(self, game_name: str, word_manager: WordManager, tiles: List[str] = None):
        """
        Generates a new game state.
        """
        self.game_name = game_name
        self.word_manager = word_manager
        if tiles:
            self.game_tiles = tiles
        else:
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
        possible_paths: List[List[int]] = None

        for character in guessed_word:
            if (possible_paths is not None) and (len(possible_paths) == 0):
                break

            character_locations = []
            for i in range(0, len(self.game_tiles)):
                if self.game_tiles[i] == character:
                    character_locations.append(i)

            if possible_paths is None:
                possible_paths = [[val] for val in character_locations]
            else:
                new_possible_paths: List[List[int]] = []
                for character_location in character_locations:
                    for possible_path in possible_paths:
                        # We cannot use the same tile multiple times in one word
                        if character_location in possible_path:
                            continue

                        # If the character location is a neighbor of the last tile on a possible
                        # path then we add this as a new possible bath for the next character
                        if GameState._tiles_are_neighbors(character_location, possible_path[-1]):
                            new_possible_path = possible_path.copy()
                            new_possible_path.append(character_location)
                            new_possible_paths.append(new_possible_path)

                possible_paths = new_possible_paths
        print(f"Possible paths for '{guessed_word}': {possible_paths}")
        return len(possible_paths) > 0

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
