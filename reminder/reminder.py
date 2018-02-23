import http.client
import json
import yaml
import time
import datetime
import psycopg2

# Import config file
with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile)

# Set Black Duck Hub variables from config.yml
blackDuckHubHost = cfg['blackduck']['hubHost']
blackDuckHubAuthToken = cfg['blackduck']['hubUserAuthToken']
reminderInterval = cfg['reminder']

### Todo - allign userId with appropriate user
hubUserId = "00000000-0000-0000-0001-000000000001"

# Set postgres variables from config.yml
DATABASE_CONFIG = {
    'host': cfg['postgres']['host'],
    'dbname': cfg['postgres']['dbname'],
    'user': cfg['postgres']['user'],
    'password': cfg['postgres']['password']
}

connect_str = "dbname=" + DATABASE_CONFIG['dbname'] +" user=" + DATABASE_CONFIG['user'] +" host=" + DATABASE_CONFIG['host'] +" password=" + DATABASE_CONFIG['password']

def checkDbForReminders():

    try:
        hubConn = http.client.HTTPSConnection(blackDuckHubHost)
        headers = {
            'authorization': blackDuckHubAuthToken,
            'cache-control': "no-cache",
        }
        hubConn.request("POST", "/api/tokens/authenticate", headers=headers)
        res = hubConn.getresponse()
        data = res.read().decode("utf-8")
        auth_obj = json.loads(data)
        bearerToken = auth_obj["bearerToken"]
        print("Hub Authorization succeeded.")

    except Exception as e:
        print("Cannot connect to Hub. Invalid token.")
        print(e)

    authHeaders = {
        'authorization': "Bearer " + bearerToken
    }

    dbConnReminder = psycopg2.connect(connect_str)
    cursorReminder = dbConnReminder.cursor()

    requestBody = {
        "content": "string",
        "contentType": "string",
        "createdAt": "2018-02-23T00:46:13.547Z",
        "notificationState": "NEW",
        "type": "POLICY_OVERRIDE"
    }

    jsonBody = json.dumps(requestBody)

    cursorReminder.execute("SELECT notification_id FROM public.notifications WHERE posted_date < now() - interval '30 days'")
    rowsTest = cursorReminder.fetchall()
    results = [item for item, in rowsTest]
    for i in range(len(results)):
        print(results[i])



while True:
    print("Checking database process running.")
    checkDbForReminders()
    time.sleep(86400)



