FROM python:3.8

WORKDIR /app


RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir kafka-python
RUN pip3 install --no-cache-dir requests

COPY ./notifier_service.py .

CMD ["python", "notifier_service.py"]