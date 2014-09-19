import os
from flask import Flask, request, Response
import json
from pygit2 import Repository, clone_repository, Commit, Tree
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
import iso8601
import os
from github3 import login
from pymongo import MongoClient

app = Flask(__name__)


@app.route('/', methods=['POST'])
def default():
    mongodb_uri = os.environ.get('MONGODB_URI')
    github_username = os.environ.get('GITHUB_USERNAME')
    github_password = os.environ.get('GITHUB_PASSWORD')
    if mongodb_uri is None or github_username is None or github_password is None:
        return Response(status=500)

    mongo_client = MongoClient(mongodb_uri)
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
                    for commit in the_repo.walk(the_repo.head.target, GIT_SORT_TIME | GIT_SORT_REVERSE):
                        the_commit = {'_sha': commit.id, 'last_updated': commit.commit_time}
                    return str(the_repo)
                except Exception as e:
                    print e.message
                    return Response("Repository " + repo + " does not exist.", status=400)
    except Exception as e:
        print e.message
        return Response("Invalid JSON. Expecting JSON of the form {\"repo\": \"user/repo\"}", status=400)

if __name__ == '__main__':
    app.run()

