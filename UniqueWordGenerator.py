import random
import string


class UniqueWordGenerator:
    def __init__(self):
        self.generated_words = set()
        self.vowels = 'aeiou'
        self.consonants = ''.join(set(string.ascii_lowercase) - set(self.vowels))

    def generate(self, length=8):
        while True:
            word = ''.join(
                random.choice(self.consonants) if i % 2 == 0 else random.choice(self.vowels)
                for i in range(length)
            ).capitalize()
            if word not in self.generated_words:
                self.generated_words.add(word)
                return word
