import os
import boto3
from flask import Flask, render_template, request, jsonify
from botocore.exceptions import ClientError

app = Flask(__name__)

# --- Configuration via environment variables ---
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "RSVP")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(TABLE_NAME)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    name = data.get("name")
    phone = data.get("phone")
    guests = data.get("guests")
    attendance = data.get("attendance")
    meal = data.get("meal")

    if not all([name, phone, guests, attendance]):
        return jsonify({"error": "Missing required fields"}), 400

    attending = attendance == "yes"

    try:
        table.put_item(
            Item={
                "phone": str(phone),
                "name": str(name),
                "guests": str(guests),
                "attendance": str(attendance),
                "attending": attending,
                "meal": str(meal) if meal else "",
            }
        )

        return jsonify({"message": "RSVP saved successfully"}), 200

    except ClientError as e:
        app.logger.error("DynamoDB error: %s", e.response["Error"]["Message"])
        return jsonify({"error": "Could not save RSVP. Please try again later."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)