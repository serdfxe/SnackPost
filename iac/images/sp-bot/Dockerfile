FROM python:3.12

WORKDIR /app/sp-bot

COPY ./sp-bot/requirements.txt /app/sp-bot
RUN pip install --no-cache-dir -r requirements.txt

COPY ./sp-bot /app/sp-bot

CMD ["/bin/bash", "-c", "python run.py"]
