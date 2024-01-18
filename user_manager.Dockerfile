FROM python:3.8

WORKDIR /app

COPY requirements.txt .
COPY ./UserManager/ ./UserManager/
COPY ./user_manager.py .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENV DATABASE_URI=mysql+pymysql://root:toor@MyTrafficDB:3306/MyTrafficDB

CMD ["python", "user_manager.py"]