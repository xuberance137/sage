import json
import sys
from datetime import datetime
import pygit2
import base64
import os.path
import gitDevMetadata
import time
from dateutil import parser
 
     
def write_tags_commits(org_name, repo_name):
    
    repo_path = './' + org_name + '/' + repo_name

    repo = pygit2.Repository(repo_path)
 
    objects = {
        'tags': [],
        'commits': [],
    }
 
    for objhex in repo:
        obj = repo[objhex]
        if obj.type == pygit2.GIT_OBJ_COMMIT:
            objects['commits'].append({
                'repo': repo_name,
                'hash': obj.hex,
                'message': obj.message,
                'commit_date': datetime.utcfromtimestamp(
                    obj.commit_time).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'author_name': obj.author.name,
                'author_email': obj.author.email,
                'parents': [c.hex for c in obj.parents],
                #'diff': repo.diff(obj.parents[0], obj),
                'files': [file.name for file in obj.tree]
            })

            # delta = repo.diff(obj.parents[0], obj)
            # delta = repo.diff(obj.parents[0], obj, cached=False, flags=0, context_lines=3, interhunk_lines=0)
            # patches = [p for p in delta]
            # print patches
            # print delta.__len__()
            # for item in delta.__iter__():
            #     print item
            
            # patches = [p for p in delta]
            # print patches
            # tree = repo.revparse_single(obj.hex).tree
            # print([(e.name, e) for e in tree])
            
        elif obj.type == pygit2.GIT_OBJ_TAG:
            objects['tags'].append({
                'repo': repo_name,
                'hex': obj.hex,
                'name': obj.name,
                'message': obj.message,
                #'target': base64.b16encode(obj.target).lower(),
                'tagger_name': obj.tagger.name,
                'tagger_email': obj.tagger.email,
            })

        else:
            # ignore blobs and trees
            pass
 
    print("Number of commits : ", len(objects["commits"]), "\t Number of tags : ", len(objects["tags"]))
    
    repo_commitlog_filename = './' + org_name + '/' + repo_name + '_tags_commits.json'
    with open(repo_commitlog_filename, 'w') as outfile:
        json.dump(objects, outfile, sort_keys = True, indent = 4)
    outfile.close()

    return

    
def commit_dev_list(org_name, repo_name):

    commit_count = 0
    dev_list = []
    
    repo_path = './' + org_name + '/' + repo_name
    
    if os.path.exists(repo_path):
     
        repo = pygit2.Repository(repo_path)
          
        for objhex in repo:

            obj = repo[objhex]

            if obj.type == pygit2.GIT_OBJ_COMMIT:
                commit_count = commit_count + 1
                dev_list.append(obj.author.name)
        
        dev_list = gitDevMetadata.derep(dev_list)

    return dev_list, commit_count, len(dev_list)
    

def build_release_timeline_tags(org_name, repo_name):

    repo_commitlog_filename = './' + org_name + '/' + repo_name + '_tags_commits.json'

    json_data = open(repo_commitlog_filename).read()
    git_data = json.loads(json_data)

    #list of release dates
    release_date_list = []
 
    commit_count = []
    file_list = []

    for commit in git_data['tags']:
        for attribute, value in commit.iteritems():
            if attribute == 'name':
                release_date_list.append(value)

    return release_date_list


def build_commit_timeline(org_name, repo_name):

    repo_commitlog_filename = './' + org_name + '/' + repo_name + '_tags_commits.json'

    json_data = open(repo_commitlog_filename).read()
    git_data = json.loads(json_data)

    commit_date_list = []

    for commit in git_data['commits']:
        for attribute, value in commit.iteritems():
            if attribute == 'commit_date':
                commit_date_list.append(parser.parse(value))

    return commit_date_list
    
    
