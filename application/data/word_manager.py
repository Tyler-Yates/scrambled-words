import os

FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))


class WordManager:
    def __init__(self):
        self.words = set()
        with open(f"{FILE_LOCATION}/../static/words.txt", mode="r") as word_file:
            for line in word_file:
                line = line.strip().upper()
                self.words.add(line)

        print(f"Loaded {len(self.words)} words.")

    def is_word(self, word: str) -> bool:
        return word in self.words
