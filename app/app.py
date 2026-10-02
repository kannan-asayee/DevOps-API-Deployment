from flask import Flask, jsonify, request
import os
import socket

app = Flask(__name__)

@app.get("/")
def home():
    return jsonify(
        service="simple-api",
        message="Simple API is running",
        hostname=socket.gethostname(),
        version=os.getenv("APP_VERSION", "dev")
    )

@app.get("/health")
def health():
    return jsonify(status="UP"), 200

@app.get("/api/v1/hello")
def hello():
    name = request.args.get("name", "DevOps")
    return jsonify(message=f"Hello {name}", api="v1")

@app.get("/api/v1/info")
def info():
    return jsonify(
        application="simple-api",
        platform="kubernetes",
        gateway="kong"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
