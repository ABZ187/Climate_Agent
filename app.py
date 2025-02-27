from flask import Flask, request, jsonify
from flask_cors import CORS
from endpoint import run_app

app = Flask(__name__)
CORS(app)  # This allows requests from your frontend


@app.route("/query", methods=["POST"])
def query():
    try:
        data = request.json
        print("Received data:", data)
        question = data.get("question")
        return jsonify({"speed test": "No question provided"}), 200
        if not question:
            return jsonify({"error": "No question provided"}), 400

        result = run_app(question)
        print("Response from run_app:", result)

        # Ensure we're returning a properly formatted response
        if isinstance(result, dict):
            response = {
                "response": {
                    "code_success": result.get("code_success", "Failed"),
                    "output": result.get("output", "No output"),
                    "code": result.get("code", "No code"),
                }
            }
        else:
            response = {"response": {"code_success": "Failed", "output": str(result)}}

        print("Sending response:", response)
        return jsonify(response)

    except Exception as e:
        print("Error occurred:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
