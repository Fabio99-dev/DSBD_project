FROM python:3.8

COPY . ./MetricsExporter

RUN pip3 install --upgrade pip
RUN pip3 install -r ./MetricsExporter/requirements.txt

EXPOSE 8000

CMD ["python", "./MetricsExporter/metrics_exporter.py"]