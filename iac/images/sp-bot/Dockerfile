FROM python:3.12

WORKDIR /app/sp-bot

COPY ./sp-bot/requirements.txt /app/sp-bot
RUN pip install --no-cache-dir -r requirements.txt

COPY ./sp-bot /app/sp-bot
COPY ./api /app/api

WORKDIR /app/sp-bot/core/sp_clients
RUN python generate_api_clients.py

WORKDIR /app/sp-bot
CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "8000"]
