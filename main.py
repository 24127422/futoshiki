from gui import FutoshikiGUI
from futoshiki import Futoshiki
import sys

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input-01.txt'
    game = Futoshiki(input_file)

    if game.size > 0:
        app = FutoshikiGUI(game)
        app.run()