from github import Github
import os
import re

import awsgi
from flask import (
    Flask,
)

import github_webhook


app = Flask(__name__)
webhook = github_webhook.Webhook(
    app,
    endpoint='/postreceive',
    secret=os.environ.get('secret'),
)

CHECKS = []

# First create a Github instance:
gh = Github(os.environ['token'])


@app.route('/')
def hello_world():
    return "Hello, World!"


@webhook.hook('ping')
def ping(payload):
    return "pong"


@webhook.hook('pull_request')
def lint(payload):
    print("Action:", payload['action'])
    if payload['action'] not in ('opened', 'synchronize'):
        return

    plpr = payload['pull_request']
    repo = gh.get_repo(plpr['base']['repo']['full_name'])
    print("repo", repo)
    commit = repo.get_commit(plpr['head']['sha'])
    print("commit", commit)
    pullreq = repo.get_pull(plpr['number'])
    print("pullreq", pullreq)

    errors = []
    try:
        for cfunc in CHECKS:
            errors += list(cfunc(commit, pullreq))
    except Exception as e:
        commit.create_status('error', description=str(e), context='lint/xonsh')
        raise
    else:
        if errors:
            commit.create_status('failure', description='\n'.join(errors), context='lint/xonsh')
        else:
            commit.create_status('success', description="PR Lint OK", context='lint/xonsh')
    print('errors', errors)


NEWS = re.compile(r"news/.*\.rst")


def has_news(commit, pullreq):
    if not any(NEWS.match(f.filename) for f in pullreq.get_files()):
        yield 'No news item'


CHECKS += [has_news]


def main(event, context):
    print("event", event)
    rv = awsgi.response(app, event, context, base64_content_types={})
    print("result", rv)
    return rv
