import time
import http.client
import json
import time
#import psycopg2

# Hub Auth
conn = http.client.HTTPSConnection("hubeval74.blackducksoftware.com")
hubUserId = "00000000-0000-0000-0001-000000000001"

headers = {
    'authorization': "token MDBjOWU1YjItOWE1OC00YTZiLWE4MzktOTE3MWZiMDg1YzI5OjIyY2Y3YTQzLTYwYTctNGQ1My05NWI5LWFiM2Q1MWRkYWRjZg==",
    'cache-control': "no-cache",
}

conn.request("POST", "/api/tokens/authenticate", headers=headers)

res = conn.getresponse()
data = res.read().decode("utf-8")
auth_obj = json.loads(data)
bearerToken = auth_obj["bearerToken"]


# Get Policy overrides
def getNewPolicyOverrideNotifications(bearerToken):
    authHeaders = {
        'authorization': "Bearer " + bearerToken
    }
    conn.request("GET", "/api/v1/users/" + hubUserId + "/notifications?limit=100&offset=0&states=NEW&filter=notificationType%3Apolicy_override", headers=authHeaders)

    res = conn.getresponse()
    data = res.read().decode("utf-8")

    notification_obj = json.loads(data)

    # Loop through notifications and find notification id and created at time
    for item in notification_obj['items']:
        print(item['notification']['id'])
        print(item['notification']['createdOn'])

        timestamp = item['notification']['createdOn']

        notificationStructure = {"id": item['notification']['id'], "createdOn": item['notification']['createdOn']}

    return

getNewPolicyOverrideNotifications(bearerToken)

# DB Connect
try:
    connect_str = "dbname='notifications' user='blackduck' host='postgres' password='blackduck'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    cursor = conn.cursor()
    print("Connected!")

except Exception as e:
    print("Uh oh, can't connect. Invalid dbname, user or password?")
    print(e)