import os
import random
from typing import List

FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))


class WordManager:
    def __init__(self):
        self.words = []
        with open(f"{FILE_LOCATION}/../static/words.txt", mode="r") as word_file:
            for line in word_file:
                line = line.strip().upper()
                self.words.append(line)

        print(f"Loaded {len(self.words)} words.")

    def get_random_words(self, number_of_words: int) -> List[str]:
        return random.sample(self.words, number_of_words)
