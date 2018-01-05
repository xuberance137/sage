# https://docs.atlassian.com/jira-software/REST/cloud/#agile/1.0/board-getAllBoards
# https://answers.atlassian.com/questions/17432852/how-to-access-issues-in-epic-via-the-api
# https://answers.atlassian.com/questions/21633354/retrieving-list-of-issues-from-a-sprint-using-jira-agile-rest-api

import requests
import requests.auth
import pycurl
from pprint import pprint
import json
from io import BytesIO
import subprocess
import cStringIO

#curl -D- -u PabloPicasso:keepmining -X GET -H "Content-Type: application/json" <URL>
# url = 'https://issues.apache.org/jira/rest/api/2/search?jql=assignee=mengxr+order+by+duedate'
#url = 'https://issues.apache.org/jira/rest/agile/1.0/board?startAt=50'
#url = 'https://issues.apache.org/jira/rest/agile/1.0/board/85/sprint/168/issue'
#url = 'https://issues.apache.org/jira/rest/api/2/issue/SPARK-1359'

# https://issues.apache.org/jira/rest/api/2/search?jql=%22Epic%20Link%22%3D12843291
# https://issues.apache.org/jira/rest/api/2/search?jql=Sprint=180

org = 'apache' #actually refers to company in heirarchy
orgID = 1
MAXPAGES = 4
MAXISSUEPAGES = 5 # max number of pages probed per sprint 
MAXITEMSPERPAGE = 50 # max from API
head_url = 'https://issues.apache.org/jira/'
headers = {'Accept': 'application/json'}
auth = ('PabloPicasso', 'keepmining')

url = 'https://issues.apache.org/jira/rest/agile/1.0/board/85/backlog?startAt=50'

def get_all_boards(org, head_url):
    
    board_list = []
    # json data object that gets written to file
    json_board_data = {
        'orgID': orgID,
        'boards': [],
    }
    
    for index in range(MAXPAGES):
        start_index = index*MAXITEMSPERPAGE
        url = head_url + 'rest/agile/1.0/board'+'?startAt='+str(start_index)
        response = requests.get(url, headers=headers, auth=auth)
        boards = json.loads(response.content)
        board_list = board_list + boards['values']

    json_board_data["boards"] = board_list
    
    with open('./apache/jira_' + org + '_' + str(orgID) + '_boards.json', 'w') as outfile:
        json.dump(json_board_data, outfile, sort_keys = True, indent = 4)
        print 'Wrote board json to file'
        outfile.close()
    
    return json_board_data
        
def get_board_sprints(org, head_url, boardIDin):
    sprint_list = []
    
    for index in range(MAXPAGES):
        start_index = index*MAXITEMSPERPAGE
        url = head_url + 'rest/agile/1.0/board/'+str(boardIDin)+'/sprint?startAt='+str(start_index)
        response = requests.get(url, headers=headers, auth=auth)
        sprints = json.loads(response.content)
        if sprints.get('values'):
            sprint = {}
            for index in range(len(sprints['values'])):
                sprint = sprints['values'][index]
                sprint['boardID'] = boardIDin
                sprint_list.append(sprint)
        else:
            #print 'No values'
            break  # no values in the sprint object
        
    print 'Number of sprints in board ' + str(boardIDin) + ' : ' + str(len(sprint_list))
    return sprint_list
    
def get_all_board_sprints(org, head_url, board_data):

    sprint_list = []
    
    json_sprint_data = {
        'sprints': [],
    }
    
    for item in board_data['boards']:
        if item['type'] == 'scrum':
            print 'board ID: ', item['id']
            sprint_list = sprint_list + get_board_sprints(org, head_url, item['id'])

    json_sprint_data["sprints"] = sprint_list
    
    with open('./apache/jira_' + org + '_' + str(orgID) + '_sprints.json', 'w') as outfile:
        json.dump(json_sprint_data, outfile, sort_keys = True, indent = 4)
        print 'Wrote sprint json to file'
        outfile.close()
            

def get_all_board_epics_sprints(org, head_url, board_data):
    
    for item in board_data['boards']:
        if item['type'] == 'scrum':
            print 'board ID: ', item['id']
            get_board_epics(org, head_url, item['id'])
            get_board_sprints(org, head_url, item['id'])

def get_board_sprint_issue_list(org, head_url, boardID):

    sprint_list = []
    
    for index in range(MAXPAGES):
        start_index = index*MAXITEMSPERPAGE
        url = head_url + 'rest/agile/1.0/board/'+str(boardID)+'/sprint?startAt='+str(start_index)
        response = requests.get(url, headers=headers, auth=auth)
        sprints = json.loads(response.content)
        if sprints.get('values'):
            sprint_list = sprint_list + sprints['values']
        else:
            break  # no values in the sprint object
        
    print 'Number of sprints : ' + str(len(sprint_list))    

    issue_list = []

    for item in sprint_list:
        url = head_url + 'rest/api/2/search?jql=Sprint='+str(item['id']) #find jql to search additional pages
        print 'Sprint ID : ', item['id']
        response = requests.get(url, headers=headers, auth=auth)
        issues = json.loads(response.content)
        if issues.get('issues'):
            issue_list = issue_list + issues['issues']

    # print issue_list
    print 'Total number of issues across sprints : ', len(issue_list)
    
    json_sprint_issue_data = {
        'board' : boardID,
        'issues': []
    }
    
    json_sprint_issue_data["issues"] = issue_list
    
    with open('./apache/jira_' + org + '_' + str(boardID) + '_sprint_issues.json', 'w') as outfile:
        json.dump(json_sprint_issue_data, outfile, sort_keys = True, indent = 4)
        print 'Wrote board sprint issue json to file'
        outfile.close()
    

def get_board_epic_issue_list(org, head_url, boardID):

    epic_list = []
    
    for index in range(MAXPAGES):
        start_index = index*MAXITEMSPERPAGE
        url = head_url + 'rest/agile/1.0/board/'+str(boardID)+'/epic?startAt='+str(start_index)
        response = requests.get(url, headers=headers, auth=auth)
        epics = json.loads(response.content)
        if epics.get('values'):
            epic_list = epic_list + epics['values']
        else:
            break  # no values in the sprint object
        
    print 'Number of epics : ' + str(len(epic_list))    

    issue_list = []

    for item in epic_list:
        # https://issues.apache.org/jira/rest/api/2/search?jql=%22Epic%20Link%22%3D12843291
        url = head_url + 'rest/api/2/search?jql=%22Epic%20Link%22%3D'+str(item['id']) #find jql to search additional pages
        print 'Epic ID : ', item['id'], url
        response = requests.get(url, headers=headers, auth=auth)
        issues = json.loads(response.content)
        if issues.get('issues'):
            issue_list = issue_list + issues['issues']

    # print issue_list
    print 'Total number of issues across epics : ', len(issue_list)
    
    json_sprint_issue_data = {
        'board' : boardID,
        'issues': []
    }
    
    json_sprint_issue_data["issues"] = issue_list
    
    with open('./apache/jira_' + org + '_' + str(boardID) + '_epic_issues.json', 'w') as outfile:
        json.dump(json_sprint_issue_data, outfile, sort_keys = True, indent = 4)
        print 'Wrote board epic issue json to file'
        outfile.close()
        
def update_board_sprint_issue_list(org, head_url, boardID):

    sprint_list = []
    
    for index in range(MAXPAGES):
        start_index = index*MAXITEMSPERPAGE
        url = head_url + 'rest/agile/1.0/board/'+str(boardID)+'/sprint?startAt='+str(start_index)
        response = requests.get(url, headers=headers, auth=auth)
        sprints = json.loads(response.content)
        if sprints.get('values'):
            sprint_list = sprint_list + sprints['values']
        else:
            break  # no values in the sprint object
        
    print 'Number of sprints : ' + str(len(sprint_list))    
    
    json_issue_data = {
        'issues': [],
    }

    for item in sprint_list:
        
        url = head_url + 'rest/api/2/search?jql=Sprint='+str(item['id']) #find jql to search additional pages

        access = False
        count = 5

        while access == False and count > 0:
            
            try:
                response = requests.get(url, headers=headers, auth=auth)
            except requests.exceptions.Timeout:
                print 'Timeout Exception on URL : ', url, ' Retrying....'
                count = count - 1
                access = False
            except requests.exceptions.TooManyRedirects:
                print 'Too many redirects. URL bad : ', url
                count = count - 5
                access = False
            except requests.exceptions.RequestException as e:
                print 'Request exception on URL :', url 
                count = count - 1
                access = False
            else:
                access = True
                issues = json.loads(response.content)
                print "Number of issues in Sprint", str(item['id']), str(item['name']), " : ", len(issues['issues'])
        
                if issues.get('issues'):
                    json_issue_data["issues"].append({
                        "sprintID" : item['id'],
                        "numIssues" : len(issues['issues']),
                        "issueList" :  issues['issues']
                        })

    with open('./apache/jira_' + org + '_' + str(boardID) + '_sprint_updated_issues.json', 'w') as outfile:
        json.dump(json_issue_data, outfile, sort_keys = True, indent = 4)
        print 'Wrote board sprint issue json to file'
        outfile.close()
            
def build_board_data_model(org, head_url, boardID):

    sprint_list = []
    
    for index in range(MAXISSUEPAGES):
        print index
        start_index = index*MAXITEMSPERPAGE
        url = head_url + 'rest/agile/1.0/board/'+str(boardID)+'/sprint?startAt='+str(start_index)
        response = requests.get(url, headers=headers, auth=auth)
        sprints = json.loads(response.content)
        if sprints.get('values'):
            sprint_list = sprint_list + sprints['values']
        else:
            break  # no values in the sprint object
        
    print 'Number of sprints : ' + str(len(sprint_list))    
    
    json_issue_data = {
        'issues': [],
    }

    for item in sprint_list:

        issue_list = []
        for index in range(MAXISSUEPAGES):
            start_index = index*MAXITEMSPERPAGE
            #find jql to search additional pages
            url = head_url + 'rest/api/2/search?jql=Sprint='+str(item['id'])+'&startAt='+str(start_index)+'&maxResults='+str(MAXITEMSPERPAGE)

            access = False
            count = 5

            while access == False and count > 0:

                try:
                    response = requests.get(url, headers=headers, auth=auth)
                except requests.exceptions.Timeout:
                    print 'Timeout Exception on URL : ', url, ' Retrying....'
                    count = count - 1
                    access = False
                except requests.exceptions.TooManyRedirects:
                    print 'Too many redirects. URL bad : ', url
                    count = count - 5
                    access = False
                except requests.exceptions.RequestException as e:
                    print 'Request exception on URL :', url
                    count = count - 1
                    access = False
                else:
                    access = True
                    issues = json.loads(response.content)
                    if issues.get('issues'):
                        for issue in issues['issues']:
                            issue_list.append(issue)
                            json_issue_data["issues"].append({
                                "boardID" : boardID,
                                "sprintID" : item['id'],
                                "issueID" : issue['id'],
                                "issueData" : issue
                            })
        
        print "Number of issues in Sprint", str(item['id']), str(item['name']), " : ", len(issue_list)

    with open('./apache/jira_' + org + '_' + str(orgID) + '_' + str(boardID) + '_issues.json', 'w') as outfile:
        json.dump(json_issue_data, outfile, sort_keys = True, indent = 4)
        print 'Wrote board sprint-based issue json to file'
        outfile.close()
        
def get_all_board_epics(org, head_url, board_data, agile_process_type):
    
    for item in board_data['boards']:
        if item['type'] == agile_process_type:
            print 'board ID: ', item['id']
            #get_board_epics(org, head_url, item['id'])
            get_board_issues(org, head_url, item['id'])

def get_board_epics(org, head_url, boardID):
    epic_list = []
    
    for index in range(MAXPAGES):
        start_index = index*MAXITEMSPERPAGE
        url = head_url + 'rest/agile/1.0/board/'+str(boardID)+'/epic?startAt='+str(start_index)
        response = requests.get(url, headers=headers, auth=auth)
        epics = json.loads(response.content)
        if epics.get('values'):
            epic_list = epic_list + epics['values']
    
    print 'Total mumber of epics : ' + str(len(epic_list))

    return epic_list
    
def get_board_issues(org, head_url, boardID):

    epic_list = get_board_epics(org, head_url, boardID)

    issue_list = []

    for index in range(len(epic_list)):
        epic = epic_list[index]
        url = head_url + 'rest/agile/1.0/board/' + str(boardID) + '/epic/' + str(epic['id']) + '/issue'
        response = requests.get(url, headers=headers, auth=auth)
        epics = json.loads(response.content)
        if epics.get('issues'):
            issue_list.append(epics['issues'])

    print 'Total number of issues in epics : ', len(issue_list)

    json_issue_data = {
        'issues': issue_list,
    }

    # with open('./apache/jira_' + org + '_' + str(orgID) + '_' + str(boardID) + '_epic_sample.json', 'w') as outfile:
    #     json.dump(json_issue_data, outfile, sort_keys = True, indent = 4)
    #     print 'Wrote board epic json to file'
    #     outfile.close()


if __name__ == '__main__':
    ORG_NAME = 'apache'        
        
#def streamline_issue_data_etl()



#get_all_board_epics(org, head_url, board_data)
#get_board_sprints(org, head_url, 104)
#get_all_board_epics_sprints(org, head_url, board_data)
#get_board_epics(org, head_url, 62)
#get_board_sprint_issue_list(org, head_url, 62)
#get_board_epic_issue_list(org, head_url, 62)
#update_board_sprint_issue_list(org, head_url, 62)

#board_data = get_all_boards(org, head_url)
#get_all_board_sprints(org, head_url, board_data)
    #build_board_data_model(org, head_url, 62)
    # get_board_issues(org, head_url, 1)
    board_data = get_all_boards(org, head_url)
    get_all_board_epics(org, head_url, board_data, 'kanban')
