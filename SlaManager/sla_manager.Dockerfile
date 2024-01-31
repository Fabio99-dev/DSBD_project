FROM python:3.8

WORKDIR /app

COPY . ./SlaManager/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./SlaManager/requirements.txt

ENV DATABASE_URI=mysql+pymysql://root:toor@SlaManagerDB:3306/SlaManagerDB
ENV PROMETHEUS_URL=http://prometheus:9090

CMD ["python", "./SlaManager/sla_manager.py"]
