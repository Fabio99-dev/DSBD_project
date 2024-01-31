FROM python:3.8

WORKDIR /app

ENV SENDER_EMAIL=mymusic56124@gmail.com
ENV EMAIL_PASSWORD="pumi jyaw fika vudo"

ENV SMTP_SERVER=smtp.gmail.com
ENV SMTP_PORT=587

COPY . ./NotifierService

RUN pip3 install --upgrade pip
RUN pip3 install -r ./NotifierService/requirements.txt


CMD ["python", "./NotifierService/notifier_service.py"]