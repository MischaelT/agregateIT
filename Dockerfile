FROM python:3.8 

WORKDIR /code/build

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# MODE=[runserver, gunicorn, celery, celerybeat, flower]
ENV MODE=runserver
ENV PYTHONPATH "/code/build/app"

CMD bash -C './start.sh'