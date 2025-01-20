FROM python:3.10
WORKDIR /app

RUN apt-get update && apt-get install -y procps

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY service1.py ./

CMD [ "python", "./service1.py" ]