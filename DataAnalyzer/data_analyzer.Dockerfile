FROM python:3.8

WORKDIR /app

COPY . ./DataAnalyzer

RUN pip3 install --upgrade pip
RUN pip3 install -r ./DataAnalyzer/requirements.txt

ENV BING_API_KEY=At71cbvTs-4zsbhV7M07ZYd41Y4FGK3PHvVOxTVZMz75lxwc1M-IQyZHypkgscJ6

CMD ["python", "./DataAnalyzer/data_analyzer.py"]