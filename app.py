from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Add a value with variables file
### The URL is't temprary ###
API_URL = "https://ph1cu2qpna.execute-api.us-east-1.amazonaws.com/RSVP"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.json

    response = requests.post(API_URL, json=data)

    if response.status_code == 200:
        return jsonify({"message": "Success"}), 200

    return jsonify({"error": "Failed"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)