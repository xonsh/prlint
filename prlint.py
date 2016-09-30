#!/usr/bin/env python2
from __future__ import print_function, absolute_import, unicode_literals, division
import sys
import os.path
import fnmatch

BASEDIR = os.path.dirname(os.path.abspath(__file__))
sys.path += [
    os.path.join(BASEDIR, 'PyGithub'),
]

from github import Github
import ConfigParser
import json
import re

NEWS = re.compile(r"news/.*\.rst")

conf = ConfigParser.SafeConfigParser()
conf.read(['xlint.conf'])

# First create a Github instance:
gh = Github(conf.get('github', 'token'))

def lint(event, context):
    print("headers", event['headers'])
    evkey = [k for k in event['headers'].keys() if k.lower() == 'x-github-event'][0]
    what = event['headers'][evkey]
    payload = json.loads(event['body'])
    print("Event:", what)
    if what == 'pull_request':
        print("Action:", payload['action'])
        if payload['action'] not in ('opened', 'synchronize'):
            return {}

        plpr = payload['pull_request']
        repo = gh.get_repo(plpr['base']['repo']['full_name'])
        print("repo", repo)
        commit = repo.get_commit(plpr['head']['sha'])
        print("commit", commit)
        pullreq = repo.get_pull(plpr['number'])
        print("pullreq", pullreq)

        errors = []
        try:
            if not any(NEWS.match(f.filename) for f in pullreq.get_files()):
                errors += ['No news item']
        except Exception, e:
            commit.create_status('error', description=str(e), context='lint/xonsh')
            raise
        else:
            if errors:
                commit.create_status('failure', description='\n'.join(errors), context='lint/xonsh')
            else:
                commit.create_status('success', description="PR Lint OK", context='lint/xonsh')
        print('errors', errors)
        return {}
    else:
        print("Not my event")
        return {}
