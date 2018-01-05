import json, pymongo
from bson import json_util
from pprint import pprint
import githubOrgMetadata
import gitDevMetadata

import time
import datetime
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as md
import seaborn as sns
import numpy as np
import pandas as pd
from scipy import stats, integrate
import re
from bson.son import SON
import scipy.stats as ss
import math
import collections

COMMIT_THRESHOLD = 2500

MIN_NUMBER_OF_SPRINTS_FOR_DIST_STAT = 15
NUMBER_OF_PAST_SPRINTS_FOR_DIST_STAT = 5
NOMINAL_DIST_STAT = 0.5
NUM_SECONDS_IN_4WKS = 2419200
NUM_SECONDS_IN_2WKS = 1209600
NUM_SECONDS_IN_1WK =   604800
TOP_DEVELOPER_COUNT = 15

# store data to mongoDB from developer JSON
def mongo_clear_collection_data(org_name):
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client[org_name]
    mongo_collection = mongo_db['boards']
    mongo_collection.drop() # throw out what's there
    mongo_collection = mongo_db['sprints']
    mongo_collection.drop() # throw out what's there
    mongo_collection = mongo_db['issues']
    mongo_collection.drop() # throw out what's there
    # close connection
    mongo_client.close()
    print "Cleared mongoDB ", org_name, " project collection"

# store data to mongoDB from developer JSON
def mongo_store_collection_data(org_name, board_json_file, sprint_json_file, issue_json_file):
    try:
        # read data from file
        data = json.load(open(board_json_file))
    except:
        print "Failed to open : ", board_json_file, " Skipping to next repo"
        return
    
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client[org_name]
    mongo_collection = mongo_db['boards']
    # load each doc into the collection
    for item in data["boards"]:
        mongo_collection.insert_one(item)
    # create index by developer name
    mongo_collection.create_index('id')

    try:
        # read data from file
        data = json.load(open(sprint_json_file))
    except:
        print "Failed to open : ", sprint_json_file, " Skipping to next repo"
        return
    
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client[org_name]
    mongo_collection = mongo_db['sprints']
    # load each doc into the collection
    for item in data["sprints"]:
        mongo_collection.insert_one(item)
    # create index by developer name
    mongo_collection.create_index('id')


    try:
        # read data from file
        data = json.load(open(issue_json_file))
    except:
        print "Failed to open : ", issue_json_file, " Skipping to next repo"
        return
    
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client[org_name]
    mongo_collection = mongo_db['issues']
    # load each doc into the collection
    for item in data["issues"]:
        mongo_collection.insert_one(item)
    # create index by developer name
    mongo_collection.create_index('issueID')

    # close connection
    mongo_client.close()
    print "Loaded mongoDB ", org_name, " board, sprint and issue collections"


# store data to mongoDB from developer JSON
def mongo_clear_issue_data(org_name):
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client[org_name]
    mongo_collection = mongo_db['issues']
    # throw out what's there
    mongo_collection.drop() 
    # close connection
    mongo_client.close()
    print "Cleared mongoDB ", org_name, " project collection"

# store data to mongoDB from developer JSON
def mongo_store_issue_data(org_name, project_json_file):
    try:
        # read data from file
        data = json.load(open(project_json_file))
    except:
        print "Failed to open : ", project_json_file, " Skipping to next repo"
        return
    
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client[org_name]
    mongo_collection = mongo_db['issues']
    # throw out what's there
    #mongo_collection.drop() 
    # load each developer into the developer collection
    for item in data["issues"]:
        mongo_collection.insert_one(item)
    # create index by developer name
    mongo_collection.create_index('issueID')
    # close connection
    mongo_client.close()
    print "Loaded mongoDB ", org_name, " project collection"
    
def mongo_load_select_project(org_name):
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client[org_name]
    except:
        print('Error: Unable to Connect to DB')
        mongo_client = None    

    data = []
    create_ts = []
    resolution_ts = []
    updated_ts = []
    values = []
    status = []
    
    if mongo_client is not None:
        doc= mongo_db["issues"].find() #{"author_name" : str(dev_name)})

        data = list(doc)    
        
        for item in data:
            create_ts.append(parser.parse(item['issueData']['fields']['created']))
            updated_ts.append(parser.parse(item['issueData']['fields']['updated']))
            status.append(item['issueData']['fields']['status']['name'])
                                 
    return create_ts, values, status

#looking for issues appearing in multiple sprints
def mongo_issue_check(org_name):
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client[org_name]
    except:
        print('Error: Unable to Connect to DB')
        mongo_client = None    

    data = []
    issueID = []
    
    if mongo_client is not None:
        doc= mongo_db["issues"].find() 

        data = list(doc)    
        print 'Number of Project Data Documents', len(data)
        
        for item in data: #iterate over sprints
            issueID.append(item['issueID'])
        
        print 'Number of issues : ', len(issueID)
        print 'Number of unique issues : ', len(gitDevMetadata.derep(issueID))
        
        pipeline = [
            {"$group": {"_id": "$issueID", "count":{"$sum":1}}},
            {"$match": {"count":{"$gt":5}}},
            {"$sort":SON([("count", -1),("_id", -1)])}
        ]
        
        count_data = list(mongo_db["issues"].aggregate(pipeline))
        
        print 'Repeat Issues :'
        
        for item in count_data:
            print item['_id'], '\t', item['count']
            
            doc= mongo_db["issues"].find({"issueID" : item['_id']})

            data = list(doc)    
            print 'Number of Repeat Issue Instances', len(data)
        
            for item2 in data:
                print item['_id'], '\t', item2['issueData']['fields']['updated']
        
        
     
def mongo_get_issue_descriptions(org_name):
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client[org_name]
    except:
        print('Error: Unable to Connect to DB')
        mongo_client = None    

    data = []
    descriptions = []
    
    if mongo_client is not None:
        doc= mongo_db["issues"].find() #{"author_name" : str(dev_name)})

        data = list(doc)    
        print 'Number of Project Data Documents : ', len(data)
        
        for item in data: #iterate over sprints
            descriptions.append(item['issueData']['fields']['description'])
            descriptions.append(item['issueData']['fields']['status']['description'])
                 
        print 'Number of issue descriptions : ', len(descriptions)
        
    return descriptions
     

def visualize_project_data_plot(timestamps, values):  


    abs_seconds = []

    for index in range(len(timestamps)):
        timestamps[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(timestamps[index])).group()
        dt = datetime.datetime.strptime(str(timestamps[index]), "%Y-%m-%d %H:%M:%S")
        abs_seconds.append(time.mktime(dt.timetuple()))

    df = pd.DataFrame({
                'timestamps': timestamps,
                'abs_time': abs_seconds,
                'values': values
            })
    sns.set(color_codes=True)
    ax = sns.jointplot(x="abs_time", y="values", data=df, marker="+")
    #ax = sns.tsplot(data = abs_seconds)
    sns.plt.show()

def visualize_issue_status_stripplot(timestamps, status):  

    timestamps = []
    abs_seconds = []
   
    for index in range(len(ts)):
        ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
        dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")

        timestamps.append(ts[index])
        abs_seconds.append(time.mktime(dt.timetuple()))
        #print timestamps[index], abs_seconds[index]
    
    df = pd.DataFrame({
        'timestamps': timestamps,
        'abs_seconds': abs_seconds,
        'status': status
        })
          
    print len(df)
      
    sns.set(style="whitegrid", color_codes=True)
    #ax = sns.stripplot(x="abs_seconds", y="status", data=df, jitter=True)
    ax = sns.stripplot(x="abs_seconds", y="status", data=df)
    sns.plt.show()


def visualize_issue_distplot(timestamps, status, status_val):  

    timestamps = []
    abs_seconds = []
    
    num_seconds_in_4wks = 2419200
   
    for index in range(len(status)):
        if status[index] == status_val:
            ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
            dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")

            timestamps.append(ts[index])
            abs_seconds.append(time.mktime(dt.timetuple()))
        #print timestamps[index], abs_seconds[index]
    
    df = pd.DataFrame({
        'timestamps': timestamps,
        'abs_seconds': abs_seconds,
        })
          
    print len(status), len(df)

    time_range = max(abs_seconds) - min(abs_seconds)
    num_bins = int(round(time_range/num_seconds_in_4wks))
    label_name = status_val + " Issue Time Distribution"  
    sns.set(color_codes=True)
    sns.distplot(abs_seconds, bins=num_bins, rug=True, label=label_name, rug_kws={"color": "r"})
    sns.plt.show()

    val = ss.binned_statistic(abs_seconds, abs_seconds, statistic='mean', bins=num_bins)

    print val


def compute_issue_distribution_indicator(timestamps, status, status_val):  

    timestamps = []
    abs_seconds = []
    
    num_seconds_in_4wks = 2419200
    num_seconds_in_2wks = 1209600
   
    for index in range(len(status)):
        if status_val =="All":
            ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
            dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")

            timestamps.append(ts[index])
            abs_seconds.append(time.mktime(dt.timetuple()))
        else:    
            if status[index] == status_val:
                ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
                dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")

                timestamps.append(ts[index])
                abs_seconds.append(time.mktime(dt.timetuple()))

    time_range = max(abs_seconds) - min(abs_seconds)
    num_bins = int(round(time_range/num_seconds_in_2wks))
    [issue_count_means, bin_edges] = np.histogram(abs_seconds, bins=num_bins) 
    print "num_bins", num_bins
    print "number of count means", len(issue_count_means)
    print issue_count_means
    
    if len(issue_count_means) > MIN_NUMBER_OF_SPRINTS_FOR_DIST_STAT:
        issue_distribution_indicator = min(np.mean(issue_count_means[-NUMBER_OF_PAST_SPRINTS_FOR_DIST_STAT:])/np.mean(issue_count_means[-MIN_NUMBER_OF_SPRINTS_FOR_DIST_STAT:]), 1.0)
    else:
        issue_distribution_indicator = NOMINAL_DIST_STAT
    
    return issue_distribution_indicator

def mongo_load_dev_activity(org_name):
    
    dev_activity = mongo_load_jira_dev_activity(org_name)
    #in future: dev activity form github will go here
    
    print 'Total number of developer activities captured : ', len(dev_activity)
    return dev_activity

def mongo_load_jira_dev_activity(org_name):
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client[org_name]
    except:
        print('Error: Unable to Connect to DB')
        mongo_client = None    

    data = []
    activity = []
    
    if mongo_client is not None:
        doc= mongo_db["issues"].find() #{"author_name" : str(dev_name)})

        data = list(doc)    
        
        for item in data:
            
            if item['issueData']['fields'].get('creator'): #creation activity
                activity_data = {
                    'dev_name' : item['issueData']['fields']['creator']['name'],
                    'activity_ts': parser.parse(item['issueData']['fields']['created']),
                    'activity_type': "Created",
                    'issue': item['issueID']
                }
                activity.append(activity_data)
            
            if item['issueData']['fields'].get('assignee'): #asignment activity: some issues don't have assignment fields
                activity_data = {
                    'dev_name' : item['issueData']['fields']['assignee']['name'],
                    'activity_ts': parser.parse(item['issueData']['fields']['created']),
                    'activity_type': "Assigned",
                    'issue': item['issueID']
                }
                activity.append(activity_data)
            
            if item['issueData']['fields'].get('comment'): #comment activity: only for issues pulled from direct issue API 2.0 which includes comments  
                for item2 in item['issueData']['fields']['comment']['comments']:
                    activity_data = {
                        'dev_name' : item2['name'],
                        'activity_ts': parser.parse(item['updated']),
                        'activity_type': "Commented",
                        'issue': item['issueID']
                    }
                    activity.append(activity_data)
            
    return activity


def compute_team_activity_distribution_indicator(activity):  

    ts = []
    timestamps = []
    abs_seconds = []
    team_members = []
    dev_activity = []
   
    for item in activity:
        team_members.append(item['dev_name'])
        ts.append(item['activity_ts'])
   
    print len(team_members)
    print len(gitDevMetadata.derep(team_members))
    print collections.Counter(team_members)
    
    for index in range(len(ts)):
        ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
        dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")
        timestamps.append(ts[index])
        abs_seconds.append(time.mktime(dt.timetuple()))

    time_range = max(abs_seconds) - min(abs_seconds)
    num_bins = int(round(time_range/NUM_SECONDS_IN_1WK))
    [activity_count_means, bin_edges] = np.histogram(abs_seconds, bins=num_bins)
    print "num_bins", num_bins
    print "number of count means", len(activity_count_means)
    print activity_count_means

    if len(activity_count_means) > MIN_NUMBER_OF_SPRINTS_FOR_DIST_STAT:
        activity_distribution_indicator = min(np.mean(activity_count_means[-NUMBER_OF_PAST_SPRINTS_FOR_DIST_STAT:])/np.mean(activity_count_means[-MIN_NUMBER_OF_SPRINTS_FOR_DIST_STAT:]), 1.0)
    else:
        activity_distribution_indicator = NOMINAL_DIST_STAT

    return activity_distribution_indicator

def compute_aggregate_dev_activity_distribution_indicator(activity):  

    team_members = []
    dev_activity = []
         
    for item in activity:
        team_members.append(item['dev_name'])
  
    top_dev_collection = collections.Counter(team_members).most_common(TOP_DEVELOPER_COUNT) 

    ts = []
    timestamps = []
    abs_seconds = []
    
    #aggregate developer activity over time for only developers that are in top developer count (ignore marginal contributors)
    for dev in top_dev_collection:
        dev_name = dev[0]
    
        for item in activity:
            if item['dev_name'] == dev_name:
                # weighting activities based on type. Creating SPs is counted as two activities relative to comments and assignments
                if item['activity_type'] == 'Created':
                    ts.append(item['activity_ts'])
                    ts.append(item['activity_ts'])
                if item['activity_type'] == 'Commented':
                    ts.append(item['activity_ts'])
                if item['activity_type'] == 'Assigned':
                    ts.append(item['activity_ts'])  

    for index in range(len(ts)):
        ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
        dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")
        timestamps.append(ts[index])
        abs_seconds.append(time.mktime(dt.timetuple()))

    time_range = max(abs_seconds) - min(abs_seconds)
    num_bins = int(round(time_range/NUM_SECONDS_IN_1WK))
    [activity_count_means, bin_edges] = np.histogram(abs_seconds, bins=num_bins)
    print activity_count_means

    if len(activity_count_means) > MIN_NUMBER_OF_SPRINTS_FOR_DIST_STAT:
        activity_distribution_indicator = min(np.mean(activity_count_means[-NUMBER_OF_PAST_SPRINTS_FOR_DIST_STAT:])/np.mean(activity_count_means[-MIN_NUMBER_OF_SPRINTS_FOR_DIST_STAT:]), 1.0)
    else:
        activity_distribution_indicator = NOMINAL_DIST_STAT

    return activity_distribution_indicator
    
if __name__ == '__main__':
    ORG_NAME = 'apache'
    
    mongo_clear_collection_data(ORG_NAME)
    mongo_store_collection_data(ORG_NAME, './apache/jira_apache_1_boards.json', './apache/jira_apache_1_sprints.json', './apache/jira_apache_1_62_issues.json')
    ## mongo_clear_issue_data(ORG_NAME)
    # mongo_store_issue_data(ORG_NAME, './apache/jira_apache_62_issue_data.json')
    #
    # ts, val, status = mongo_load_select_project(ORG_NAME)
    # visualize_issue_distplot(ts, status, "Resolved")
    # visualize_issue_status_stripplot(ts, status)

    # visualize_project_data_plot(ts, val)
    # desc = mongo_get_issue_descriptions(ORG_NAME)
    
    # mongo_issue_check(ORG_NAME)
    
    # ts, val, status = mongo_load_select_project(ORG_NAME)
    
    # dist_indicator = compute_issue_distribution_indicator(ts, status, "All")
    # print dist_indicator
    
    # dist_indicator = compute_issue_distribution_indicator(ts, status, "Resolved")
    # print dist_indicator
    
    # dist_indicator = compute_issue_distribution_indicator(ts, status, "Open")
    # print dist_indicator


    # activity_list = mongo_load_dev_activity(ORG_NAME)

    # dist_indicator = compute_team_activity_distribution_indicator(activity_list)
    # print dist_indicator
    
    # dist_indicator = compute_aggregate_dev_activity_distribution_indicator(activity_list)
    # print dist_indicator
    
    
        
