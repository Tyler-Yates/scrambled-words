import logging
import random
from collections import Counter
from threading import Timer
from typing import List, Set, Dict

from application.data.word_manager import WordManager
from application.util.time_util import get_time_millis

TOTAL_TILES = 25
TOTAL_TIME_SECONDS = 3 * 60

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

        self.game_tiles: List[str] = []
        self.expire_time: int = None
        self.valid_guesses: Dict[str, Set[str]] = {}
        self.word_counter: Counter = Counter()
        self.game_running = True

        # TODO save scores server-side
        self.scores: Dict[str, int] = {}

        self.new_board(tiles)

    def new_board(self, tiles: List[str] = None):
        if tiles:
            self.game_tiles = tiles
        else:
            self.game_tiles = GameState._generate_tiles()

        self.word_counter = Counter()
        self.game_running = True

        self.expire_time = get_time_millis() + (TOTAL_TIME_SECONDS * 1000)
        end_game_timer = Timer(TOTAL_TIME_SECONDS, self.end_game)
        end_game_timer.start()

        # Dictionary from player ID to Set of valid guesses
        self.valid_guesses = {}

        self._log_info("Created new board")

    def end_game(self):
        self.game_running = False
        self._log_info("Game ended")

    def get_game_state(self, player_id: str = None):
        game_state = {"expire_time": self.expire_time, "tiles": self.game_tiles}
        if player_id:
            game_state["player_guesses"] = self.valid_guesses.get(player_id, [])
        else:
            # No player_id indicates a reset of the game so send empty guesses list
            game_state["player_guesses"] = []
        return game_state

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
        # Ensure the guessed word is all lower-case to match with the tiles
        guessed_word = guessed_word.lower()

        # Ensure players are not able to guess after the game has expired
        if not self.game_running:
            self._log_info(f"{player_id} guess word '{guessed_word}' was guessed after game ended")
            return False

        # Ensure players cannot guess the same word multiple times
        if guessed_word in self.valid_guesses.get(player_id, set()):
            self._log_info(f"{player_id} guess word '{guessed_word}' has already been guessed successfully by player")
            return False

        # Check if the word is recognized and on the board
        if self.word_manager.is_word(guessed_word):
            word_is_on_board = self._word_is_on_board(guessed_word)
            if word_is_on_board:
                self._log_info(f"{player_id} guess word '{guessed_word}' is a valid word")

                # Increase the word counter to make it easier to calculate point at the end of the game
                self.word_counter[guessed_word] += 1

                if player_id in self.valid_guesses:
                    self.valid_guesses.get(player_id).add(guessed_word)
                else:
                    valid_guesses = set()
                    valid_guesses.add(guessed_word)
                    self.valid_guesses[player_id] = valid_guesses
            else:
                self._log_info(f"{player_id} guess word '{guessed_word}' is not on the board")

            return word_is_on_board
        else:
            self._log_info(f"{player_id} guess word '{guessed_word}' is not a recognized word")
            return False

    def get_score_state(self, player_id: str) -> Dict[str, object]:
        scored_words = []
        unscored_words = []
        valid_guesses = self.valid_guesses.get(player_id, set())
        for valid_guess in valid_guesses:
            if self.word_counter.get(valid_guess) == 1:
                scored_words.append(valid_guess)
            else:
                unscored_words.append(valid_guess)

        return {"scored_words": scored_words, "unscored_words": unscored_words}

    def _word_is_on_board(self, guessed_word: str) -> bool:
        possible_paths: List[List[int]] = None

        # Iterate through each character of the guessed word
        for character in guessed_word:
            # Terminate early if we have no possible paths
            if (possible_paths is not None) and (len(possible_paths) == 0):
                break

            # Find all locations where the current character is on the board.
            character_locations = []
            for i in range(0, len(self.game_tiles)):
                if self.game_tiles[i] == character:
                    character_locations.append(i)

            if possible_paths is None:
                # The first character will not have any previous character positions to check.
                possible_paths = [[val] for val in character_locations]
            else:
                # Create a new list for possible paths so that previous paths that will not
                # work with the new character positions are discarded.
                new_possible_paths: List[List[int]] = []

                # Check each character position to see if it can be appended to a possible path.
                for character_location in character_locations:
                    for possible_path in possible_paths:
                        # We cannot use the same tile multiple times in one word.
                        if character_location in possible_path:
                            continue

                        # If the character location is a neighbor of the last tile on a possible
                        # path then we add this as a new possible bath for the next character.
                        if GameState._tiles_are_neighbors(character_location, possible_path[-1]):
                            new_possible_path = possible_path.copy()
                            new_possible_path.append(character_location)
                            new_possible_paths.append(new_possible_path)

                # Swap in the new possible paths to discard paths that are no longer possible.
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
        for i in range(0, TOTAL_TILES):
            tiles.append(
                random.choice(
                    [
                        "a",
                        "a",
                        "a",
                        "a",
                        "b",
                        "c",
                        "d",
                        "d",
                        "e",
                        "e",
                        "e",
                        "e",
                        "e",
                        "f",
                        "g",
                        "h",
                        "h",
                        "h",
                        "i",
                        "i",
                        "i",
                        "i",
                        "j",
                        "k",
                        "l",
                        "l",
                        "m",
                        "n",
                        "o",
                        "o",
                        "o",
                        "o",
                        "q",
                        "r",
                        "r",
                        "s",
                        "s",
                        "s",
                        "s",
                        "t",
                        "t",
                        "t",
                        "u",
                        "u",
                        "u",
                        "v",
                        "w",
                        "x",
                        "y",
                        "z",
                    ]
                )
            )
        return tiles
