# Example usage:
# python githubDevMetadataVisualizer.py python-repos youtube-dl
# assuming youtube_dl is located in the python-repos folder. Python-repos is a generic org name to hold the youtube-dl project repo

import sys
import os
import githubOrgMetadata
import gitRepoMetadata
import gitDevMetadata
import githubMongoAccess
import matplotlib.pyplot as plt
from dateutil import parser

API_ACCESS_TOKEN = 'be7509f8c67110aa61782bcd9e21b37fa66d5c16'

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("USAGE: {0} <org_name> <repo_name>".format(__file__))
        print("Example: python github_data_aggregator.py Mozilla firefox")
        sys.exit(0)

    org_name = sys.argv[1]
    repo_name = sys.argv[2]

    # gitRepoMetadata.write_tags_commits(org_name, repo_name)

    release_list = gitRepoMetadata.build_release_timeline_tags(org_name, repo_name)
    release_date_list = []

    for item in release_list:
        date = list(item)  
        #date_s = date[0]+date[1]+date[2]+date[3]+'-'+date[5]+date[6]+'-'+date[8]+date[9]+'T00:00:00Z'
        date_s = date[0]+date[1]+date[2]+date[3]+'-'+date[5]+date[6]+'-'+date[8]+date[9]+' 00:00:00'
        release_date_list.append(date_s)

    print len(release_date_list)
    release_date_list = gitDevMetadata.derep(release_date_list)
    print len(release_date_list)

    commit_date_list = gitRepoMetadata.build_commit_timeline(org_name, repo_name)
    print len(commit_date_list)

    # for item in commit_date_list: print item

    githubMongoAccess.plot_timeline_hist(commit_date_list, release_date_list)