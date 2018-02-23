import http.client
import json
import yaml
import time
import datetime
import psycopg2
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

    time.sleep(15)

    dbConnReminder = psycopg2.connect(connect_str)
    cursorReminder = dbConnReminder.cursor()

    cursorReminder.execute("SELECT notification_id, project_id, project_version_id FROM public.notifications")
    rowsTest = cursorReminder.fetchall()

    for i in range(len(rowsTest)):
        projectId = rowsTest[i][1]
        projectVersionId = rowsTest[i][2]
        projectLink = "https://" + blackDuckHubHost + "/api/projects/" + projectId + "/versions/" + projectVersionId
        print(projectLink)



while True:
    print("Checking database process running.")
    checkDbForReminders()
    time.sleep(86400)



