FROM python:3.8

WORKDIR /app

COPY . ./RouteHandler/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./RouteHandler/requirements.txt

ENV DATABASE_URI=mysql+pymysql://root:toor@RoutesDB:3306/RoutesDB

CMD ["python", "./RouteHandler/route_handler.py"]