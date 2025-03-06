from flask import Flask, request, jsonify
from flask_cors import CORS
from endpoint import run_app
from datetime import datetime

# Configure logging
import logging
import os

logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)  # This allows requests from your frontend


@app.route("/query", methods=["POST"])
def query():
    try:
        data = request.json
        question = data.get("question")
        if not question:
            return jsonify({"error": "No question provided"}), 400

        # Log the time of query received and the input query
        logger.info(f"Query received: {question}")
        result = run_app(question)

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

        # Log the time of output sent and the response
        logger.info(f"Response sent: {response}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
