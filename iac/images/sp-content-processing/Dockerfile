FROM python:3.12

WORKDIR /app/sp-content-processing

COPY ./sp-content-processing/requirements.txt /app/sp-content-processing
RUN pip install --no-cache-dir -r requirements.txt

COPY ./sp-content-processing /app/sp-content-processing

CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "8000"]
