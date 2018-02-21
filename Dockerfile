FROM python:3
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["./wait-for-it.sh", "db:5432", "--", "python", "app.py"]