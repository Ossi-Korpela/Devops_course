FROM python:3.10
WORKDIR /app

RUN apt-get update && apt-get install -y procps && apt-get install -y docker.io docker-compose

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "service1.py" ]