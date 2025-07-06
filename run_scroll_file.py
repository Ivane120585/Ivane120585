import sys
from scroll_wrapped_codex.scribe_codex import ScribeCodex
from scroll_wrapped_codex.lashon_compiler import compile_lashon

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_scroll_file.py <filename.scroll>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)

    compiled = compile_lashon(lines)
    scribe = ScribeCodex()

    for line in compiled:
        result = scribe.execute(line)
        print(result)

if __name__ == "__main__":
    main() 