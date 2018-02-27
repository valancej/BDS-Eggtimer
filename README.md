# Python & Postgres 

## Services:
* fetchnotifications: Fetches new policy overrides every five minutes
* reminder: Reminds user of policy overrides after elapsed period of time

## Location of Docker Hub images:

* https://hub.docker.com/r/jvalance/hub-timer-fetch
* https://hub.docker.com/r/blackducksoftware/hub-timer-reminder

```
docker-compose build
docker-compose up
```