import os
from flask import Flask, request, Response
import json
from pygit2 import Repository, clone_repository, Commit, Tree
from pygit2 import GIT_SORT_TIME, GIT_SORT_REVERSE
import os
from github3 import login
import time
from pymongo import MongoClient
from datetime import datetime, timedelta
import shutil
import re
import dateutil.parser
import logging
# from celery import Celery
import threading


# def make_celery(app):
#     celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#     class ContextTask(TaskBase):
#         abstract = True
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#     celery.Task = ContextTask
#     return celery

app = Flask(__name__)
# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379',
#     CELERY_RESULT_BACKEND='redis://localhost:6379'
# )
# celery = make_celery(app)


# @celery.task()

mongodb_uri = os.environ.get('MONGOLAB_URI')
github_username = os.environ.get('GITHUB_USERNAME')
github_password = os.environ.get('GITHUB_PASSWORD')
db = MongoClient(mongodb_uri).get_default_database()


# add 1 second, since we don't want to get the last commit when polling the API
# commit_time_plus_one_sec = datetime.fromtimestamp(commit_time + 1)

def convert_time_to_iso8601(commit_time):
    date_str_without_timezone = datetime.fromtimestamp(commit_time).isoformat()
    timezone_offset = time.strftime("%z")
    return date_str_without_timezone + timezone_offset


# example: 2014-09-17T07:34:03-0500, so we replace :03- with :04-
def increment_iso8601_second(iso8601_str):
    date = dateutil.parser.parse(iso8601_str) + timedelta(seconds=1)
    return date.isoformat()


def get_commits_for_repo(the_repo):
    commit_list = []
    for commit in the_repo.walk(the_repo.head.target, GIT_SORT_TIME | GIT_SORT_REVERSE):
        the_commit = {'sha': str(commit.id), 'date': convert_time_to_iso8601(commit.commit_time)}
        commit_list.append(the_commit)
    return commit_list


@app.route('/', methods=['POST'])
def default():
    if mongodb_uri is None or github_username is None or github_password is None:
        return Response("Environment variables not set.", status=500)
    else:
        try:
            repo_name = validate_and_return_repo(request.get_json(force=True))
            repo_in_db = db.repositories.find_one({"_id": repo_name})

            if repo_in_db is None:
                # thr = threading.Thread(target=do_stuff, args=repo_name)
                # thr.start()

                return Response("Repository %s added to watch list" % repo_name, status=200)
            else:
                raise RuntimeError("Repository " + repo_name + " is already being watched.")
        except Exception as e:
            shutil.rmtree('./temp_repo', ignore_errors=True)
            print(e)
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

def do_stuff(repo_name):
    the_repo = clone_repository('git://github.com/' + repo_name + '.git', 'temp_repo')
    commit_list = get_commits_for_repo(the_repo)
    latest_commit = commit_list[-1]
    latest_commit_date = latest_commit['date']
    db.repositories.insert({"_id": repo_name, "last_updated": increment_iso8601_second(latest_commit_date),
                                        "commits": commit_list})
    shutil.rmtree('./temp_repo', ignore_errors=True)
