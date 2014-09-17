import os
from flask import Flask, request, Response
import json

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def default():
    if request.method == 'GET':
        return "hello!"
    if request.method == 'POST':
        try:
            jsonData = request.get_json(force=True)
            if len(jsonData) != 2:
                return Response("Invalid JSON. Expecting JSON of the form {\"repo\": \"user/repo\"}", status=400)
            else:
                repo = str(jsonData['repo'])
                vcs = str(jsonData['vcs'])
                splitRepo = repo.split('/')
                if len(splitRepo) != 2:
                    return Response("Repository must have the form user/repo. Example: mdotson/metrics-dashboard",
                                    status=400)
                else:

        except Exception:
            return Response("Invalid JSON. Expecting JSON of the form {\"repo\": \"user/repo\"}", status=400)
        # repoName = jsonData['repo']
        # print("hey")

