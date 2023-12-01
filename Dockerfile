FROM python:3.11

ENV APP_HOME /app

WORKDIR $APP_HOME

COPY . .

RUN pip install -r requirements.txt

RUN mkdir -p storage && touch storage/data.json

EXPOSE 5000

ENTRYPOINT ["python", "main.py"]