import requests
from pprint import pprint
import json
from io import BytesIO
import subprocess
import os


def store_repo_md(org_name):
    # REST API query: #repos?page=2&per_page=100
    # Writing repo metadata for a particular org to json file for load and ETL later. 100 is the page size limit for github API
    # TODO: Need to find a way to automatically find how many pages to crawl
    N_PAGES = 7 # totals to a mx of 100 repos
    org_repo = []
    org_repo_md_filename = './' + org_name + '/' + org_name + '_repos.json'
    directory = os.path.dirname(org_repo_md_filename)

    if not os.path.exists(directory):
        os.makedirs(directory)

    for PAGE in range(1, N_PAGES):
        print("Org Rep List Page", PAGE)
        dictionary = requests.get('https://api.github.com/orgs/' + org_name + '/repos?page=' + str(PAGE) + '&per_page=20').json()
        print(len(dictionary))
        org_repo = org_repo + dictionary

        with open(org_repo_md_filename, 'w') as outfile:
            json.dump(org_repo, outfile, sort_keys = True, indent = 4)
            outfile.close()
    
    print("Number of projects in stored repo : ", len(org_repo))
    return org_repo
    
def load_repo_md(org_name):

    org_repo = []
    org_repo_md_filename = './' + org_name + '/' + org_name + '_repos.json'
    with open(org_repo_md_filename) as infile:
        org_repo = json.load(infile)
        infile.close()

    print("Number of projects in loaded repo : ", len(org_repo))
    return org_repo

def clone_repo(org_name, org_repo, clone_flag):
    
    cloned_repo_list = []
    
    for index in range(len(org_repo)):
        if clone_flag == True:
            print("Repo ", index)
            clone_cmd = 'git clone ' + org_repo[index]["clone_url"] + ' ./' + org_name + '/' + org_repo[index]["name"]
            print("Clone command line : ", clone_cmd)
            subprocess.call(clone_cmd, shell=True)
        cloned_repo_list.append(str(org_repo[index]["name"]))
        
    return cloned_repo_list

def build_language_repo_list(org_name, language):

    repo_list = []
    org_repo = []

    org_repo_md_filename = './' + org_name + '/' + org_name + '_repos.json'

    with open(org_repo_md_filename) as infile:
        org_repo = json.load(infile)
        infile.close()

    for repo in org_repo:
        if repo['language'] == language:
            repo_list.append(repo['name'])

    return repo_list


