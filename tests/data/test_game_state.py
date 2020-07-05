from typing import List

from application import WordManager
from data.game_state import GameState
from tests.data.test_word_manager import TestWordManager


class TestGameState:
    def setup_method(self):
        # Create a word manager that accepts any word
        word_manager = TestWordManager()

        tiles = [
            "s", "a", "b", "e", "r",
            "j", "t", "t", "s", "x",
            "z", "z", "z", "z", "z",
            "s", "z", "z", "z", "z",
            "z", "z", "z", "z", "z"
        ]

        self.game_state = GameState("test", word_manager, tiles)

    def test_guess_word_valid(self):
        assert self.game_state.guess_word("player", "set") is True
        assert self.game_state.guess_word("player", "states") is True

    def test_guess_word_invalid(self):
        assert self.game_state.guess_word("player", "armory") is False
        assert self.game_state.guess_word("player", "test") is False

    def test_guess_word_unrecognized(self):
        self.game_state.word_manager = WordManager({"test"})
        assert self.game_state.guess_word("player", "word") is False

    def test_word_is_on_board_valid(self):
        assert self.game_state._word_is_on_board("set") is True
        assert self.game_state._word_is_on_board("sat") is True
        assert self.game_state._word_is_on_board("state") is True
        assert self.game_state._word_is_on_board("states") is True
        assert self.game_state._word_is_on_board("rest") is True
        assert self.game_state._word_is_on_board("saber") is True
        assert self.game_state._word_is_on_board("stab") is True
        assert self.game_state._word_is_on_board("best") is True
        assert self.game_state._word_is_on_board("bat") is True
        assert self.game_state._word_is_on_board("bats") is True

    def test_word_is_on_board_invalid(self):
        assert self.game_state._word_is_on_board("armory") is False

    def test_word_is_on_board_invalid_reuse(self):
        assert self.game_state._word_is_on_board("test") is False
        assert self.game_state._word_is_on_board("jaba") is False

    def test_tiles_are_neighbors_0(self):
        TestGameState._assert_neighbors(0, [1, 5, 6])

    def test_tiles_are_neighbors_1(self):
        TestGameState._assert_neighbors(1, [0, 2, 5, 6, 7])

    def test_tiles_are_neighbors_4(self):
        TestGameState._assert_neighbors(4, [3, 8, 9])

    def test_tiles_are_neighbors_7(self):
        TestGameState._assert_neighbors(7, [1, 2, 3, 6, 8, 11, 12, 13])

    def test_tiles_are_neighbors_20(self):
        TestGameState._assert_neighbors(20, [15, 16, 21])

    def test_tiles_are_neighbors_23(self):
        TestGameState._assert_neighbors(23, [17, 18, 19, 22, 24])

    def test_tiles_are_neighbors_24(self):
        TestGameState._assert_neighbors(24, [18, 19, 23])

    @staticmethod
    def _assert_neighbors(starting_tile: int, neighbors: List[int]):
        for i in range(0, 25):
            if i == starting_tile:
                continue

            if i in neighbors:
                assert GameState._tiles_are_neighbors(starting_tile, i) is True
            else:
                assert GameState._tiles_are_neighbors(starting_tile, i) is False
