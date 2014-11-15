import os
from flask import Flask, request, Response, jsonify
import json
from github3 import login
from pygit2 import Repository, clone_repository, Commit, Tree
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
import os
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import shutil
import dateutil.parser
import threading
import uuid


app = Flask(__name__)

github_username = os.environ.get('GITHUB_USERNAME')
github_password = os.environ.get('GITHUB_PASSWORD')
gh = login(github_username, password=github_password)

# mongodb_uri = os.environ.get('MONGOLAB_URI')
# db = MongoClient(mongodb_uri).get_default_database()
db = MongoClient()['default']

# main loop
# while True:
#     time.sleep(1)

def convert_time_to_iso8601(commit_time):
    date_str_without_timezone = datetime.fromtimestamp(commit_time).isoformat()
    timezone_offset = time.strftime("%z")
    return date_str_without_timezone + timezone_offset


# we want to increment, because when we do API calls with the since parameter, it is inclusive rather than exclusive
def increment_iso8601_second(iso8601_str):
    date = dateutil.parser.parse(iso8601_str) + timedelta(seconds=1)
    return date.isoformat()


def get_commits_for_repo(the_repo, repo_name):
    commit_list = []
    for commit in the_repo.walk(the_repo.head.target, GIT_SORT_TIME | GIT_SORT_REVERSE):
        the_commit = {'_id': str(commit.id), 'repo': repo_name, 'date': convert_time_to_iso8601(commit.commit_time)}
        commit_list.append(the_commit)
    return commit_list

@app.route('/', methods=['GET'])
def get():
    repos = db.repositories.find()
    return jsonify(repos)

@app.route('/', methods=['POST'])
def default():
    # if mongodb_uri is None:
    #     return Response("Environment variables not set.", status=500)
    # else:
    directory_uuid = str(uuid.uuid4())
    try:
        repo_name = validate_and_return_repo(request)
        repo_in_db = db.repositories.find_one({"_id": repo_name})

        if repo_in_db is None:
            thr = threading.Thread(target=do_stuff, args=[repo_name, directory_uuid])
            thr.daemon = True
            thr.start()

            return Response("Repository %s added to watch list" % repo_name, status=200)
        else:
            raise RuntimeError("Repository " + repo_name + " is already being watched.")
    except Exception as e:
        shutil.rmtree('./' + directory_uuid, ignore_errors=True)
        return Response(e.message, status=400)


def try_parsing_json(request):
    try:
        return request.get_json()
    except Exception as e:
        raise RuntimeError("Invalid JSON.")


def validate_and_return_repo(request):
    json_data = try_parsing_json(request)
    if json_data is None:
        raise RuntimeError("Must specify Content-Type type of 'application/json'")
    if len(json_data) != 1:
        raise RuntimeError("Invalid JSON. Expecting JSON of the form {\"repo\": \"user/repo\"}")
    else:
        repo = str(json_data['repo'])
        split_repo = repo.split('/')
        if len(split_repo) != 2:
            raise RuntimeError("Repository must have the form user/repo. Example: mdotson/metrics-dashboard")
        else:
            the_repo = gh.repository(split_repo[0], split_repo[1])
            if the_repo is None:
                raise RuntimeError("Repository %s does not exist" % repo)
            else:
                return repo


def do_stuff(repo_name, directory_uuid):
    the_repo = clone_repository('git://github.com/' + repo_name + '.git', directory_uuid)
    commit_list = get_commits_for_repo(the_repo, repo_name)
    latest_commit = commit_list[-1]
    latest_commit_date = latest_commit['date']
    db.commits.insert(commit_list)
    db.repositories.insert({"_id": repo_name, "last_updated": increment_iso8601_second(latest_commit_date),
                            "commit_count": len(commit_list)})
    shutil.rmtree('./' + directory_uuid, ignore_errors=True)