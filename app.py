# app.py

import sys
from controllers.main_controller import MainController

def main():
    if len(sys.argv) < 2:
        print("Usage: python app.py <collection_filename>")
        sys.exit(1)
    collection_filename = sys.argv[1]
    controller = MainController(collection_filename)
    exit_code = controller.run()
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
