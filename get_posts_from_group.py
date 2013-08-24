""" This script is used to get all the post from a group using users access token. This script also saves those individual posts into individual files"""

import facebook as fb
import argparse
import os
import json
import time
import sys
import codecs

parser = argparse.ArgumentParser(description="Passing the parameters")

# Get the access token
parser.add_argument('access_token',type=str,default=None,help='Access Token')

# Connection type
parser.add_argument('--conn_type',type=str,default='groups',help='The type of connection')

# Fields required to avoid unnecessary netwrok load
parser.add_argument('--fields',nargs='*', type=str, help='Fields to filter (to get only those fields in the response)')

# get the group information
parser.add_argument('--group_id',type=str,help='id of the group')
parser.add_argument('--group_name',type=str,help='Name of the group')

# get the member information (to filter posts based on member)
parser.add_argument('--member_id',type=str,help='Group member id')
parser.add_argument('--member_name',type=str,help='Group member name')

# Save path
parser.add_argument('--savedir', type=str, help='Path to save the posts to...')

graphURL = "https://graph.facebook.com"

def trimURL(url):
    return url.replace(graphURL,"",1)

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
    
def createURL(group_id, data_type, fields):
    newURL = os.path.join("",group_id,data_type)
    #newURL += "?fields="
    #field = ','.join(fields)
    #newURL += field
    #print newURL
    return newURL

    
def get_feed_from_group(graph, url, member_id):
    if not group_id:
        print "Invalid Group id! Exiting..."
        time.sleep(2)
        sys.exit(0)
    else:
        not_done = True
        while not_done:
            feeds = graph.request(url)
            if feeds['data']:
                filtered = [f for f in feeds['data'] if f['from']['id'] == '100000153068470']
            else:
                not_done = False
            
            if filtered:
                for feed in filtered:
                    #print feed['message']
                    #feed['message'] = feed['message'].encode('UTF-8')
                    #print feed['message']
                    with open(os.path.join(args.savedir,feed['created_time']+".json"),'w') as f:
                        json.dump(feed,f)
            
            # Go to next page
            nextPage = feeds['paging']['next']
            url = trimURL(nextPage)
        

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
    
    # Create URL with fields
    #url = createURL(group_id,"feed",args.fields)
    #ags={}
    #for f in args.fields:
    #    ags['fields'] = f
    url = os.path.join(group_id,'feed')
    #print ags
    #This function will get the feeds from facebook group and save each of them as a single file
    get_feed_from_group(graph, url, args.member_id)