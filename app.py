import time
import http.client
import json
import time
import psycopg2
import threading



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


# DB Connect
try:
    connect_str = "dbname='notifications' user='blackduck' host='postgres' password='blackduck'"
    # use our connection values to establish a connection
    conn = psycopg2.connect(connect_str)
    cursor = conn.cursor()
    print("Connected!")
    cursor.execute("""CREATE TABLE IF NOT EXISTS notifications (id serial primary key, posted_date date not null, notification_id varchar(255) not null)""")
    cursor.execute("INSERT INTO public.notifications (posted_date, notification_id) VALUES (%s, %s)", ('2018-01-22', 'fjdaklfjadkls'))
    cursor.execute("""SELECT * FROM notifications""")
    rows = cursor.fetchall()
    print(rows)

except Exception as e:
    print("Uh oh, can't connect. Invalid dbname, user or password?")
    print(e)


# Get Policy overrides
def getNewPolicyOverrideNotifications(bearerToken):
    threading.Timer(5.0, getNewPolicyOverrideNotifications).start()
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
        ts = time.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
        formattedTimeStamp = time.strftime("%Y-%m-%d", ts)
        print(formattedTimeStamp)



getNewPolicyOverrideNotifications(bearerToken)