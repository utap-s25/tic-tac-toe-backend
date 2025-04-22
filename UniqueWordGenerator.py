import random
import string

word_list = None

def load_word_list():
    global word_list
    import urllib.request

    word_url = "https://www.mit.edu/~ecprice/wordlist.10000"
    response = urllib.request.urlopen(word_url)
    long_txt = response.read().decode()
    word_list = long_txt.splitlines()

class UniqueWordGenerator:
    def __init__(self):
        self.generated_words = set()

    def generate(self, min_length=8):
        word = ""
        first = True
        while len(word) < min_length:
            if first:
                first = False
            else:
                word += "."     # Concat via "." for ease of typing an readability
            temp_word = "x" * min_length
            while len(temp_word) > min_length:  # Make sure the word is a reasonable length
                temp_word = random.choice(word_list)
            word += temp_word
        if word in self.generated_words:
            return self.generate(min_length)    # If we already used this, just generate again
        self.generated_words.add(word)
        return word

load_word_list()
