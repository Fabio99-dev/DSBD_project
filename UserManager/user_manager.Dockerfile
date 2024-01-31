FROM python:3.8

WORKDIR /app

COPY ./ ./UserManager/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./UserManager/requirements.txt

ENV DATABASE_URI=mysql+pymysql://root:toor@MyTrafficDB:3306/MyTrafficDB

CMD ["python", "./UserManager/user_manager.py"]