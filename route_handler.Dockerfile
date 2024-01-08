FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URI=mysql+pymysql://root:toor@RoutesDB:3306/RoutesDB

CMD ["python", "route_handler.py"]