import http.client
import json
import time
import datetime
import psycopg2
import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Set Black Duck Hub variables from config file
blackDuckHubHost = os.environ["BLACK_DUCK_HUB_HOST"]
blackDuckHubAuthToken = os.environ["BLACK_DUCK_HUB_AUTH_TOKEN"]
reminderInterval = os.environ['REMINDER']

### Todo - allign userId with appropriate user
hubUserId = "00000000-0000-0000-0001-000000000001"

# Set postgres variables from config.yml
DATABASE_CONFIG = {
    'host': os.environ["POSTGRES_HOST"],
    'dbname': os.environ["POSTGRES_DB"],
    'user': os.environ["POSTGRES_USER"],
    'password': os.environ["POSTGRES_PASSWORD"]
}

connect_str = "dbname=" + DATABASE_CONFIG['dbname'] +" user=" + DATABASE_CONFIG['user'] +" host=" + DATABASE_CONFIG['host'] +" password=" + DATABASE_CONFIG['password']

##
# Email
##
senderEmail = os.environ["EMAIL_SENDER"]
recipientEmail = os.environ["EMAIL_RECIPIENT"]
msg = MIMEMultipart('alternative')
msg['Subject'] = os.environ["EMAIL_SUBJECT"]
msg['From'] = senderEmail
msg['To'] = recipientEmail

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

    # Need to configure interval. Should be fine for demo purposes
    print(reminderInterval)
    cursorReminder.execute("""SELECT notification_id, project_id, project_version_id FROM public.notifications WHERE posted_date < now() - interval %s""", [reminderInterval])
    #cursorReminder.execute("SELECT notification_id, project_id, project_version_id FROM public.notifications")
    rowsTest = cursorReminder.fetchall()

    if rowsTest:

        print("Notifications found. Sending email.")    
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()      
        mail.login(os.environ["EMAIL_LOGIN"], os.environ["EMAIL_PASSWORD"])

        for i in range(len(rowsTest)):
            projectId = rowsTest[i][1]
            projectVersionId = rowsTest[i][2]
            projectLink = "https://" + blackDuckHubHost + "/api/projects/" + projectId + "/versions/" + projectVersionId
            html = """
            <html>
                <head></head>
                <body>
                    <p>Black Duck Policy Violation Reminder</p>
                    <p>Visit project <a href="{0}">{0}</a></p>
                </body>
            </html>
            """
            final_html = html.format(projectLink)
            messagePart = MIMEText(final_html, 'html')
            msg.attach(messagePart)
            mail.sendmail(senderEmail, recipientEmail, msg.as_string())
        mail.quit()

    else:
        print("No notifications found. Will retry soon.")


while True:
    print("Checking database process running.")
    checkDbForReminders()
    time.sleep(86400)