import json, pymongo
from bson import json_util
from pprint import pprint
import githubOrgMetadata


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

COMMIT_THRESHOLD = 2500

# store data to mongoDB from developer JSON
def mongo_clear_developer_data(org_name):
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client[org_name]
    mongo_collection = mongo_db['developers']
    # throw out what's there
    mongo_collection.drop() 
    # close connection
    mongo_client.close()
    print "Cleared mongoDB ", org_name, " developer collection"

# store data to mongoDB from developer JSON
def mongo_store_developer_data(dev_json_file):
    try:
        # read data from file
        data = json.load(open(dev_json_file))
    except:
        print "Failed to open : ", dev_json_file, " Skipping to next repo"
        return
    
    # put in specific mongoDB collection
    mongo_client = pymongo.MongoClient('localhost', 27017)
    mongo_db = mongo_client['Mozilla']
    mongo_collection = mongo_db['developers']
    # throw out what's there
    #mongo_collection.drop() 
    # load each developer into the developer collection
    for item in data["developers"]:
        mongo_collection.insert_one(item)
    # create index by developer name
    mongo_collection.create_index('author_name')
    # close connection
    mongo_client.close()


def mongo_load_developer_data():
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client['Mozilla']
    except:
        print('Error: Unable to Connect')
        mongo_client = None    

    data = []
    
    if mongo_client is not None:
        doc= mongo_db["developers"].find()

        data = list(doc)
        t = json_util.dumps(data)
        for item in data:
            for key, value in item.iteritems():
                if key == 'author_name':
                    print value
        #json.dumps(data, sort_keys=True, indent=4)    

def mongo_load_developer_data_filter():
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client['Mozilla']
    except:
        print('Error: Unable to Connect')
        mongo_client = None    

    data = []
    dev_list = []
    
    if mongo_client is not None:
        doc= mongo_db["developers"].find({"commit_count": {"$gt":COMMIT_THRESHOLD}})

        data = list(doc)
        t = json_util.dumps(data)
        for item in data:
            for key, value in item.iteritems():
                if key == 'author_name':
                    print value
                    dev_list.append(value)
        
        return dev_list

def mongo_load_select_developer(dev_name):
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client['Mozilla']
    except:
        print('Error: Unable to Connect')
        mongo_client = None    

    data = []
    timestamps = []
    values = []
    
    if mongo_client is not None:
        doc= mongo_db["developers"].find({"author_name" : str(dev_name)})

        data = list(doc)
        for item in data:
            for key, value in item.iteritems():
                if key == 'commit_times':
                    for timeitem in value:
                        # print timeitem, parser.parse(timeitem)
                        timestamps.append(parser.parse(timeitem))
                        values.append(1)
        #json.dumps(data, sort_keys=True, indent=4) 
    return timestamps, values
    
    
def mongo_load_developer_pd():
    try:
        mongo_client = pymongo.MongoClient('localhost', 27017)
        mongo_db = mongo_client['Mozilla']
    except:
        print('Error: Unable to Connect')
        mongo_client = None    

    data = []
    timestamp_count = []
    author_name = []
    touch_list_count = []
    commit_count = []
    
    if mongo_client is not None:
        doc= mongo_db["developers"].find()

        data = list(doc)
        for item in data:
            for key, value in item.iteritems():
                if key == 'author_name':
                    author_name.append(value)
                if key == 'commit_times':
                    timestamp_count.append(len(value))
                if key == 'file_touch_list':
                    touch_list_count.append(len(value))
                if key == 'commit_count':
                    commit_count.append(value)
        
        print "Number of developers in DataFrame : ", len(author_name)
                    
        df = pd.DataFrame({
                    'author_name': author_name,
                    'timestamp_count': timestamp_count,
                    'touch_list_count': touch_list_count,
                    'commit_count': commit_count
        })

    #print df
    
    sns.set(color_codes=True)
    
    #ax = sns.regplot(x="commit_count", y="touch_list_count", data=df, marker="+")
    
    #ax = sns.tsplot(data = commit_count)

    ax = sns.distplot(commit_count, bins=500, kde=False, rug=True)

    
    # sns.distplot(touch_list_count, rug=True, label=" touch list")
    # plt.legend()
    
    # ax = sns.jointplot(x="commit_count", y="touch_list_count", data=df,
    #                     marginal_kws=dict(bins=100, rug=True),
    #                     annot_kws=dict(stat="r"),
    #                     s=40, edgecolor="w", linewidth=1
    #                 )
    #
    #ax = sns.jointplot(x="commit_count", y="touch_list_count", data=df, kind="reg")
    
    # sns.pairplot(df)
    # plt.xlim(0, 40000)
    # plt.ylim(0, 2000)
    
    #sns.jointplot(x="commit_count", y="touch_list_count", data=df, kind="hex", color='g')
    axes = ax.axes
    axes.set_xlim(0, 500)
    #axes.set_ylim(0, 2000)
    #ax.set(xlabel='Developer Commit Count', ylabel='File Touch Count')    
    sns.plt.show()

def visualize_dev_commit_simple_plot(timestamps, values):  
        
    sns.set(color_codes=True)
    plt.subplots_adjust(bottom=0.2)
    plt.xticks( rotation=25 )
    ax=plt.gca()
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(timestamps,values, 'ro') #c=sns.color_palette()[2])
    plt.show()

    
def visualize_dev_data_plot(timestamps, values):  

    abs_seconds = []

    for index in range(len(timestamps)):
        timestamps[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(timestamps[index])).group()
        dt = datetime.datetime.strptime(str(timestamps[index]), "%Y-%m-%d %H:%M:%S")
        abs_seconds.append(time.mktime(dt.timetuple()))
        print timestamps[index], abs_seconds[index]

    df = pd.DataFrame({
                'timestamps': timestamps,
                'abs_time': abs_seconds,
                'values': values
            })
    sns.set(color_codes=True)
    ax = sns.jointplot(x="abs_time", y="values", data=df, marker="+")
    #ax = sns.tsplot(data = abs_seconds)
    sns.plt.show()


def visualize_dev_commit_stripplot(dev_list):  

    timestamps = []
    abs_seconds = []
    dev_name = []

    for dev in dev_list:
        
        ts, values = mongo_load_select_developer(dev)
    
        for index in range(len(ts)):
            ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
            dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")

            timestamps.append(ts[index])
            abs_seconds.append(time.mktime(dt.timetuple()))
            dev_name.append(dev)
            #print timestamps[index], abs_seconds[index]
    
    df = pd.DataFrame({
        'timestamps': timestamps,
        'abs_seconds': abs_seconds,
        'dev_name': dev_name
        })
          
    print len(df)
      
    sns.set(style="whitegrid", color_codes=True)
    ax = sns.stripplot(x="abs_seconds", y="dev_name", data=df, jitter=True)
    sns.plt.show()  


def visualize_dev_commit_interval(dev_list):  

    timestamps = []
    abs_seconds = []
    dev_name = []
    commit_interval = []

    for dev in dev_list:
        
        ts, values = mongo_load_select_developer(dev)
    
        ts.sort(reverse=True)

        for index in range(len(ts)):
            ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(ts[index])).group()
            dt = datetime.datetime.strptime(str(ts[index]), "%Y-%m-%d %H:%M:%S")

            timestamps.append(ts[index])
            abs_seconds.append(time.mktime(dt.timetuple()))
            dev_name.append(dev)
            #print timestamps[index], abs_seconds[index]
        # abs_seconds.sort()
        for index in range(len(abs_seconds)):
            if index == 0:
                commit_interval.append(1000)
            else:
                commit_interval.append(abs_seconds[index-1] - abs_seconds[index])
        
    df = pd.DataFrame({
        'timestamps': timestamps,
        'abs_seconds': abs_seconds,
        'dev_name': dev_name
        })
          
    print len(df)
      
    #sns.set(style="whitegrid", color_codes=True)
    #ax = sns.stripplot(x="abs_seconds", y="dev_name", data=df, jitter=True)
    sns.set(color_codes=True)
    ax =sns.distplot(commit_interval, rug=True, label="Commit Intervals", bins=1000, kde=False)
    axes = ax.axes
    axes.set_xlim(0, 2000000)
    sns.plt.show()  



def visualize_dev_data(timestamps, values):  

    df = pd.DataFrame({
                'timestamps': timestamps,
                'values': values
    })
    
    print type(df)
    print df

def plot_timeline_hist(commit_ts, release_ts):  

    abs_seconds = []
    type_ts = []

    num_seconds_in_4wks = 2419200
    num_seconds_in_2wks = 1209600
    num_samples = 1000
   
    # index commits and mark type
    for index in range(len(commit_ts)):
        commit_ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(commit_ts[index])).group()
        dt = datetime.datetime.strptime(str(commit_ts[index]), "%Y-%m-%d %H:%M:%S")
        abs_seconds.append(time.mktime(dt.timetuple()))
        type_ts.append('commit')

    # index releases and mark type
    for index in range(len(release_ts)):
        release_ts[index] = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d', str(release_ts[index])).group(0)
        try:
            dt = datetime.datetime.strptime(str(release_ts[index]), "%Y-%m-%d %H:%M:%S")
        except:
            release_ts[index] = release_ts[index-1]
            # raise
        abs_seconds.append(time.mktime(dt.timetuple()))
        type_ts.append('release')

    #form tuples with timestamps and types and sort on timestamps
    timestamps = zip(abs_seconds, type_ts)
    sorted_timestamps = sorted(timestamps, key=lambda timestamps: timestamps[0], reverse=True)
    limited_timestamps = sorted_timestamps[0:num_samples]
    #split back to timestamps and tuples after sorting
    abs_seconds, type_ts = [v[0] for v in limited_timestamps], [v[1] for v in limited_timestamps]

    # #binning to create histograms/time series
    # time_range = max(abs_seconds) - min(abs_seconds)
    # num_bins = int(round(time_range/num_seconds_in_4wks))
    # [issue_count_means, bin_edges] = np.histogram(abs_seconds, bins=num_bins) 
    # print "num_bins", num_bins
    # print "number of count means", len(issue_count_means)
    # print issue_count_means
    # label_name = " Commit Time Distribution"  
    # sns.set(color_codes=True)
    # sns.distplot(abs_seconds, bins=num_bins, rug=True, label=label_name, rug_kws={"color": "r"})
    # sns.plt.show()

    
    df = pd.DataFrame({
        'abs_seconds': abs_seconds,
        'type': type_ts
        })
          
    print len(df)
      
    sns.set(style="whitegrid", color_codes=True)
    ax = sns.stripplot(x="abs_seconds", y="type", data=df, jitter=False)
    sns.plt.show()  




if __name__ == '__main__':

    org_name = 'Mozilla'
    org_repo = githubOrgMetadata.load_repo_md(org_name)

    # mongo_clear_developer_data(org_name)
    #
    # for index in range(0, 50):
    #     repo_name = org_repo[index]["name"]
    #     repo_dev_filename = './' + org_name + '/' + repo_name + '_developers.json'
    #     print repo_dev_filename
    #     mongo_store_developer_data(repo_dev_filename)

    #
    # mongo_load_developer_data()
    # mongo_load_developer_pd()

    dev_name = 'Jeff Hammel'
    dev_list = mongo_load_developer_data_filter()

    print dev_list
    print len(dev_list)

    #visualize_dev_commit_stripplot(dev_list)
    visualize_dev_commit_interval(dev_list)
    # timestamps, values = mongo_load_select_developer(dev_name)
    # visualize_dev_data_plot(timestamps, values)


