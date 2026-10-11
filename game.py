import random
from words import WORDS, HINTS
from stats import SessionStats

DIFFICULTIES = {
    "easy": {"lives": 8, "base_points": 5},
    "medium": {"lives": 6, "base_points": 10},
    "hard": {"lives": 4, "base_points": 15},
}


class HangmanGame:
    def __init__(self):
        self.stats = SessionStats()
        self.score = 0
        self.streak = 0
        self.difficulty = "medium"
        self.category = "technology"
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = DIFFICULTIES[self.difficulty]["lives"]
        self.hint_used = False

    def start_round(self):
        self.secret = random.choice(WORDS[self.category])
        self.guessed.clear()
        self.wrong.clear()
        self.lives = DIFFICULTIES[self.difficulty]["lives"]
        self.hint_used = False

    def masked(self):
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        if len(letter) != 1 or not letter.isalpha():
            return "Enter one letter."
        letter = letter.lower()
        if letter in self.guessed or letter in self.wrong:
            return "Already guessed."
        if letter in self.secret:
            self.guessed.add(letter)
            return "Correct."
        self.wrong.add(letter)
        self.lives -= 1
        return "Wrong."

    def use_hint(self):
        if self.hint_used:
            return None
        self.hint_used = True
        self.score = max(0, self.score - 2)
        return HINTS.get(self.secret, "No hint available.")

    def play_round(self):
        self.start_round()
        while self.lives > 0 and not self.won():
            print("\nWord:", self.masked())
            print("Wrong:", " ".join(sorted(self.wrong)) or "-")
            print("Lives:", self.lives, "Score:", self.score, "Streak:", self.streak)
            raw = input("Letter, /hint, or /quit: ").strip().lower()
            if not raw:
                print("Please enter a letter, /hint, or /quit.")
                continue
            if raw == "/quit":
                return False
            if raw == "/hint":
                hint = self.use_hint()
                if hint:
                    print(f"Hint (-2 pts): {hint}")
                else:
                    print("Hint already used this round.")
                continue
            if raw.startswith("/"):
                print("Unknown command. Valid commands: /hint, /quit")
                continue
            print(self.guess(raw))

        if self.won():
            self.streak += 1
            pts = DIFFICULTIES[self.difficulty]["base_points"] + self.streak
            self.score += pts
            self.stats.record(True, self.streak)
            print("Solved:", self.secret)
            return True

        self.stats.record(False, self.streak)
        self.streak = 0
        print("Out of lives. The word was:", self.secret)
        return True

    def choose_difficulty(self):
        diff_names = "/".join(DIFFICULTIES.keys())
        while True:
            raw = input(f"\nChoose difficulty ({diff_names}) or press Enter to keep [{self.difficulty}]: ").strip().lower()
            if not raw:
                return True
            if raw in ("q", "quit", "/quit"):
                return False
            if raw in DIFFICULTIES:
                self.difficulty = raw
                return True
            print("Unknown difficulty. Please choose from:", ", ".join(DIFFICULTIES.keys()))

    def choose_category(self):
        while True:
            print("\nCategories:", ", ".join(WORDS))
            raw = input("Choose category or q: ").strip().lower()
            if raw in ("q", "quit", "/quit"):
                return None
            if raw in WORDS:
                return raw
            print("Unknown category. Please choose from:", ", ".join(WORDS))

    def ask_replay(self):
        while True:
            again = input("\nAnother round? [y/n]: ").strip().lower()
            if again in ("y", "yes"):
                return True
            if again in ("n", "no"):
                return False
            print("Invalid input. Please enter 'y' or 'n'.")

    def print_summary(self):
        print("\n=== Session Statistics ===")
        print(f"Rounds played : {self.stats.rounds}")
        print(f"Wins          : {self.stats.wins}")
        print(f"Win percentage: {self.stats.win_percentage:.1f}%")
        print(f"Best streak   : {self.stats.best_streak}")
        print(f"Total score   : {self.score}")

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")
        while True:
            if not self.choose_difficulty():
                self.print_summary()
                return

            category = self.choose_category()
            if category is None:
                self.print_summary()
                return
            self.category = category

            if not self.play_round():
                self.print_summary()
                return

            if not self.ask_replay():
                self.print_summary()
                return
