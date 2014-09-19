import os
from flask import Flask, request, Response
import json
from pygit2 import Repository, clone_repository
from pygit2 import GIT_SORT_TOPOLOGICAL, GIT_SORT_REVERSE

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def default():
    if request.method == 'GET':
        return "hello!"
    if request.method == 'POST':
        try:
            jsonData = request.get_json(force=True)
            if len(jsonData) != 1:
                print "hello1"
                return Response("Invalid JSON. Expecting JSON of the form {\"repo\": \"user/repo\"}", status=400)
            else:
                print "hello2"
                repo = str(jsonData['repo'])
                splitRepo = repo.split('/')
                if len(splitRepo) != 2:
                    return Response("Repository must have the form user/repo. Example: mdotson/metrics-dashboard",
                                    status=400)
                else:
                    print "hello4"
                    try:
                        the_repo = clone_repository('git://github.com/' + repo + '.git', 'temp_repo')
                        return str(the_repo)
                    except Exception as e:
                        return Response("Repository " + repo + " does not exist.", status=400)
        except Exception as e:
            print e.message
            return Response("Invalid JSON. Expecting JSON of the form {\"repo\": \"user/repo\"}", status=400)

if __name__ == '__main__':
    app.run()

