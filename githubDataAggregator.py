import sys
import os
import githubOrgMetadata
import gitRepoMetadata
import gitDevMetadata
import matplotlib.pyplot as plt

API_ACCESS_TOKEN = 'be7509f8c67110aa61782bcd9e21b37fa66d5c16'

CLONE = True

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("USAGE: {0} <org_name> <repo_name>".format(__file__))
        print("Example: python github_data_aggregator.py Mozilla firefox")
        sys.exit(0)

    org_name = sys.argv[1]
    repo_name = sys.argv[2]
    
    if CLONE:
        org_repo = githubOrgMetadata.store_repo_md(org_name)
        repo_md = githubOrgMetadata.load_repo_md(org_name)
        cloned_repo_list = githubOrgMetadata.clone_repo(org_name, repo_md, CLONE)
        print(cloned_repo_list)
        
        for index in range(len(cloned_repo_list)):
            print(index, cloned_repo_list[index])

        repo_path = './' + org_name + '/' + repo_name
        print("Walking Metadata for repo @ ", repo_path)
        
        gitRepoMetadata.write_tags_commits(org_name, repo_name)
        gitDevMetadata.commit_dev_etl(org_name, repo_name)

    commit_count = []

    for index in range(len(cloned_repo_list)):
        print(index)
        repo_name  = cloned_repo_list[index]
        dev_list, num_commits, num_devs = gitRepoMetadata.commit_dev_list(org_name, repo_name)
        commit_count.append((repo_name, num_commits, num_devs))

    #print commit_count

    commit_count = sorted(commit_count, key=lambda commit: commit[1], reverse=True)

    print(commit_count[0][0])

    print([i[2] for i in commit_count]) 
    plt.plot([i[2] for i in commit_count], [i[1] for i in commit_count], 'ro')
    plt.show()

    dev_data = gitDevMetadata.build_repo_dev_data(org_name, commit_count[0][0])