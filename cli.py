import sys
from scroll_wrapped_codex.scribe_codex import ScribeCodex

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py \"Anoint: Your command here\"")
        sys.exit(1)

    command = sys.argv[1]
    scribe = ScribeCodex()
    result = scribe.execute(command)
    print(result)

if __name__ == "__main__":
    main() 