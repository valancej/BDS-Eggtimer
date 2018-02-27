# Black Duck Eggtimer
* Remind user of policy overrides via email

## Services:
* fetchnotifications: Fetches new policy overrides every five minutes
* reminder: Reminds user of policy overrides after elapsed period of time

## Location of Docker Hub images:

* https://hub.docker.com/r/jvalance/hub-timer-fetch
* https://hub.docker.com/r/jvalance/hub-timer-reminder

## Installation instructions

* Clone repo
* Edit hub-config.env file
* Run command below

```
docker-compose up
```