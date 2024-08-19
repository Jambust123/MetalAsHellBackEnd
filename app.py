from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api')
def home():
    return "Welcome to the Metal As Hell API!"

if __name__ == '__main__':
    app.run(debug=True)

