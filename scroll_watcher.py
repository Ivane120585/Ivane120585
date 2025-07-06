import time, os
from scroll_wrapped_codex.scribe_codex import ScribeCodex
from scroll_wrapped_codex.lashon_compiler import compile_lashon

WATCH_FOLDER = "scrolls/"
scribe = ScribeCodex()
seen = set()

while True:
    files = [f for f in os.listdir(WATCH_FOLDER) if f.endswith(".scroll")]
    for fname in files:
        path = os.path.join(WATCH_FOLDER, fname)
        if path not in seen:
            with open(path) as f:
                compiled = compile_lashon(f.readlines())
                for line in compiled:
                    print(scribe.execute(line))
            seen.add(path)
    time.sleep(5) 