FROM python:3.12

WORKDIR /app/sp-user

COPY ./sp-user/requirements.txt /app/sp-user
RUN pip install --no-cache-dir -r requirements.txt

COPY ./sp-user /app/sp-user

RUN alembic upgrade head

VOLUME /app/sp-user/logs

CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "8000"]
