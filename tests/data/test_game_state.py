from typing import List

from data.game_state import GameState


class TestGameState:
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
