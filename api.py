from flask import Flask, request, jsonify
from scroll_wrapped_codex.scribe_codex import ScribeCodex

app = Flask(__name__)
scribe = ScribeCodex()

@app.route("/execute", methods=["POST"])
def execute():
    data = request.json
    command = data.get("scroll", "")
    result = scribe.execute(command)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run() 