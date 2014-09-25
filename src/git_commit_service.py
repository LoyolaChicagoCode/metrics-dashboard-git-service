import os
from flask import Flask, request, Response
import json
from pygit2 import Repository, clone_repository, Commit, Tree
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
import os
from github3 import login
import time
from pymongo import MongoClient
from datetime import datetime, tzinfo
import shutil


app = Flask(__name__)


def convert_time(commit_time):
    date_without_timezone = str(datetime.fromtimestamp(commit_time).isoformat())
    timezone_offset = time.strftime("%z")
    return date_without_timezone + timezone_offset

@app.route('/', methods=['POST'])
def default():

    mongodb_uri = os.environ.get('MONGOLAB_URI')
    github_username = os.environ.get('GITHUB_USERNAME')
    github_password = os.environ.get('GITHUB_PASSWORD')
    if mongodb_uri is None or github_username is None or github_password is None:
        return Response("Environment variables not set.", status=500)
    else:
        try:
            mongo_client = MongoClient(mongodb_uri) # ok
            repo = validate_and_return_repo(request.get_json(force=True)) # ok
            the_repo = clone_repository('git://github.com/' + repo + '.git', 'temp_repo')
            commit_list = []
            for commit in the_repo.walk(the_repo.head.target, GIT_SORT_TIME | GIT_SORT_REVERSE):
                the_commit = {'sha': str(commit.id), 'last_updated': convert_time(commit.commit_time)}
                commit_list.append(the_commit)
            db = mongo_client.get_default_database()



            the_one = db.repositories.find_one({"_id": repo})
            if the_one is None:
                latest_commit = commit_list[-1]
                latest_commit_date = latest_commit['last_updated']
                x = db.repositories.insert({"_id": repo, "last_update": latest_commit_date, "commits": commit_list})



                # x = db.hello.insert({"commits": commit_list})
                # remove temp_repo, just needed the information
                shutil.rmtree('./temp_repo', ignore_errors=True)
                return Response(str(x), status=200)
            else:
                raise RuntimeError("Repository " + repo + " is already being watched.")
        except Exception as e:
            shutil.rmtree('./temp_repo', ignore_errors=True)
            return Response(e.message, status=400)

def validate_and_return_repo(json):
    if len(json) != 1:
        raise RuntimeError("Invalid JSON. Expecting JSON of the form {\"repo\": \"user/repo\"}")
    else:
        repo = str(json['repo'])
        split_repo = repo.split('/')
        if len(split_repo) != 2:
            raise RuntimeError("Repository must have the form user/repo. Example: mdotson/metrics-dashboard")
        else:
            return repo