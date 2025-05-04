FROM python:3.12

WORKDIR /app/sp-scraper

COPY ./sp-scraper/requirements.txt /app/sp-scraper
RUN pip install --no-cache-dir -r requirements.txt

COPY ./sp-scraper /app/sp-scraper

CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "8000"]
