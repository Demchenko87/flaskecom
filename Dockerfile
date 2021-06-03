FROM python:3.9.5
COPY . .
RUN pip install -r requirements.txt
