FROM python:3.9-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY service1.py ./

CMD [ "python", "./service1.py" ]