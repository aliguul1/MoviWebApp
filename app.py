from flask import Flask

app = Flask(__name__)

# This is a "Route" - it tells Flask what to do when someone visits the main page
@app.route('/')
def home():
    return "<h1>Welcome to MoviWeb!</h1><p>The movie app is loading...</p>"

if __name__ == '__main__':
    # debug=True allows the server to auto-restart when you save changes
    app.run(debug=True, port=5000)