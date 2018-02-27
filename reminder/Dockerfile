FROM jvalance/hub-timer-fetch:latest
ADD . /code
WORKDIR /code
CMD ["./wait-for-it.sh", "db:5432", "--", "python", "-u", "reminder.py"]