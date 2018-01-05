import json
import os
from pprint import pprint
import radon.complexity as rd

def derep(seq):
    """
    Makes a list unique
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]


def commit_dev_etl(org_name, repo_name):

    repo_commitlog_filename = './' + org_name + '/' + repo_name + '_tags_commits.json'

    json_data = open(repo_commitlog_filename).read()
    git_data = json.loads(json_data)

    #list of devs
    dev_list = []
    # json data object that gets written to file
    json_dev_data = {
        'developers': [],
    }
 
    commit_count = []
    file_list = []

    for commit in git_data['commits']:
        for attribute, value in commit.items():
            if attribute == 'author_name':
                dev_list.append(value)
     
    dev_list =derep(dev_list)        
    print("Number of Commits : ", len(git_data['commits']), "\t Number of unique developers : ", len(dev_list))
    
    for dev in dev_list:
        file_touch_list = []
        messages = []
        commit_times = []
        commit_hashes = []
        count = 0
        for commit in git_data['commits']:
            for attribute, value in commit.items():
                if value == dev:
                    count = count + 1
                    file_touch_list = file_touch_list + commit['files']
                    messages.append(commit['message'])
                    commit_times.append(commit['commit_date'])
                    commit_hashes.append(commit['hash'])
                    author_email = commit['author_email']
                    
        json_dev_data["developers"].append({
            'author_name': dev,
            'author_email': author_email,
            'commit_count': count,
            'file_touch_list': file_touch_list,
            'messages': messages,
            'commit_times': commit_times,
            'commit_hashes': commit_hashes,
            'commit_repo': commit['repo'] 
            })

    repo_dev_filename = './' + org_name + '/' + repo_name + '_developers.json'
    with open(repo_dev_filename, 'w') as outfile:
        json.dump(json_dev_data, outfile, sort_keys = True, indent = 4)
    outfile.close()

    return


def build_repo_dev_data(org_name, repo_name):

    repo_commitlog_filename = './' + org_name + '/' + repo_name + '_tags_commits.json'

    json_data = open(repo_commitlog_filename).read()
    git_data = json.loads(json_data)

    #list of devs
    dev_list = []
    dev_commits_list = []
    # json data object that gets written to file
    json_dev_data = {
        'developers': [],
    }
 
    for commit in git_data['commits']:
        if commit.get('author_name'):
            dev_list.append(commit['author_name'])
     
    dev_list =derep(dev_list)        
    print("Number of Commits : ", len(git_data['commits']), "\t Number of unique developers : ", len(dev_list))
    
    for dev in dev_list:
        messages = []
        commits = []
        commit_times = []
        commit_hashes = []
        count = 0
        for commit in git_data['commits']:
            if commit.get('author_name'):
                if commit['author_name'] == dev:
                    count = count + 1
                    file_list = []
                    if commit.get('files'):
                        for file in commit['files']:
                            if file.endswith('.py'):
                                file_list.append(file)

                    commits.append({
                        'time': commit['commit_date'],
                        'hash': commit['hash'],
                        'message': commit['message'],
                        'files': file_list
                        })
                    author_email = commit['author_email']
                    
        json_dev_data["developers"].append({
            'author_name': dev,
            'author_email': author_email,
            'commit_count': count,
            'commits': commits,
            'commit_repo': commit['repo'] 
            })

        dev_commits_list.append((dev, count))

    repo_dev_filename = './' + org_name + '/' + repo_name + '_dev_data.json'
    with open(repo_dev_filename, 'w') as outfile:
        json.dump(json_dev_data, outfile, sort_keys = True, indent = 4)
    outfile.close()

    print('Wrote dev data file to : ', repo_dev_filename)

    return json_dev_data, dev_commits_list


def radon_test(org_name, repo_name, file_name):
    file_name = './' + org_name + '/' + repo_name + '/' + file_name
    print(file_name)

    # clone_cmd = 'git show ' + org_repo[index]["clone_url"] + ' ./' + org_name + '/' + org_repo[index]["name"]
    # print "Clone command line : ", clone_cmd
    # subprocess.call(clone_cmd, shell=True)
    file_data = open(file_name).read()
    print(file_data)
    cc = rd.cc_rank(file_data)
    print(cc)










