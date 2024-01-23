FROM python:3.8

RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir psutil
RUN pip3 install --no-cache-dir prometheus_client
RUN pip3 install --no-cache-dir requests
RUN pip3 install --no-cache-dir kafka-python

COPY cpu_exporter.py .

EXPOSE 8000

CMD ["python", "cpu_exporter.py"]