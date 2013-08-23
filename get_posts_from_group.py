""" This script is used to get all the post from a group using users access token. This script also saves those individual posts into individual files"""

import facebook as fb
import argparse
import os
import json
import time
import sys

parser = argparse.ArgumentParser(description="Passing the parameters")

# Get the access token
parser.add_argument('access_token',type=str,default=None,help='Access Token')

# Connection type
parser.add_argument('--conn_type',type=str,default='groups',help='The type of connection')

# get the group information
parser.add_argument('--group_id',type=str,help='id of the group')
parser.add_argument('--group_name',type=str,help='Name of the group')

# get the member information (to filter posts based on member)
parser.add_argument('--member_id',type=str,help='Group member id')
parser.add_argument('--member_name',type=str,help='Group member name')

def trimURL(url):
    return url.replace("https://graph.facebook.com","",1)

def get_user(graph):
    return graph.get_object('me')
    
def get_connection(graph, conn_type):
    return graph.get_connections('me',conn_type)
    
def get_group_id(graph, groups, group_name):
    
    if not groups:
        print "No data in Groups found! Exiting..."
        time.sleep(2)
        sys.exit(0)
    elif not group_name:
        print "Group Name not specified! Exiting..."
        time.sleep(2)
        sys.exit(0)
    
    # Do the work 
    not_found = True
    while not_found:
        if not groups['data']:
            print "No such group found! Exiting..."
            time.sleep(2)
            sys.exit(0)
        else:    
            for g in groups['data']:
                if g['name'] == group_name:
                    gid = g['id']
                    not_found = False
                    break
            else:
                newURL = trimURL(groups['paging']['next'])
                print newURL
                groups = graph.request(newURL)
    # Return the group id!
    return gid    
    
    
def get_feed_from_group(graph, group_id):
    
    if not group_id:
        print "Invalid Group id! Exiting..."
        time.sleep(2)
        sys.exit(0)
    else:
        feeds = graph.request(os.path.join(group_id,'feed'))
        print [data['message'] for data in feeds['data'] if data['from']['id'] == '100000153068470']

if __name__ == '__main__':
    args = parser.parse_args()
    
    if not args.access_token:
        print "Access token is required!  Exiting..."
        time.sleep(2)
        sys.exit(0)
        
    # Get the GraphAPI object
    graph = fb.GraphAPI(args.access_token)
    
    user = get_user(graph)
    groups = get_connection(graph, conn_type = args.conn_type)
    
    # Search for group
    group_id = get_group_id(graph, groups, group_name=args.group_name)
    
    #This function will get the feeds from facebook group and save each of them as a single file
    get_feed_from_group(graph, group_id)