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

def checkDbForReminders():

    dbConnReminder = psycopg2.connect(connect_str)
    cursorReminder = dbConnReminder.cursor()

    cursorReminder.execute("SELECT notification_id FROM public.notifications WHERE posted_date < now() - interval '1 days'")
    rowsTest = cursorReminder.fetchall()
    print(rowsTest)


while True:
    print("Checking database process running.")
    checkDbForReminders()
    time.sleep(10000)



