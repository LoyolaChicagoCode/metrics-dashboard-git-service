from flask import Flask, request, Response


app = Flask(__name__)


@app.route('/', methods=['GET'])
def default():
    return Response("Hello!", status=200)