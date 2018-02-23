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

# DB Connect
try:
    dbConn = psycopg2.connect(connect_str)
    cursor = dbConn.cursor()
    print("Database connection succeeded.")
    cursor.execute("""CREATE TABLE IF NOT EXISTS public.notifications (id serial primary key, posted_date date not null, notification_id varchar(255) unique not null)""")
    dbConn.commit()
    cursor.close()
    dbConn.close()
except Exception as e:
    print("Cannot connect to database. Invalid dbname, user or password.")
    print(e)


# Get Policy overrides
def getNewPolicyOverrideNotifications():

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
    
    hubConn.request("GET", "/api/v1/users/" + hubUserId + "/notifications?limit=100&offset=0&states=NEW&filter=notificationType%3Apolicy_override", headers=authHeaders)

    res = hubConn.getresponse()
    data = res.read().decode("utf-8")
    notification_obj = json.loads(data)

    # If new policy overrides found, check db and loop through
    if notification_obj['items']:
        dbConnNotification = psycopg2.connect(connect_str)
        cursorNotification = dbConnNotification.cursor()
        
        for item in notification_obj['items']:
            timestamp = item['notification']['createdOn']
            ts = time.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
            formattedTimestamp = time.strftime("%Y%m%d", ts)
            finalTimestamp = datetime.datetime.strptime(formattedTimestamp, '%Y%m%d').date()
            cursorNotification.execute("INSERT INTO public.notifications (posted_date, notification_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (finalTimestamp, item['notification']['id']))

        
        dbConnNotification.commit()
        cursorNotification.execute("""SELECT * FROM notifications""")
        rows = cursorNotification.fetchall()
        print(rows)
        cursorNotification.close()
        dbConnNotification.close()

while True:
    print("Policy check process running.")
    getNewPolicyOverrideNotifications()
    time.sleep(300)


# Check the database for possible reminders
