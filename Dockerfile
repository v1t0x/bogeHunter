FROM python:3.12-slim

WORKDIR /app

COPY bogebot.py .

RUN pip install requests beautifulsoup4 flask

EXPOSE 8080

CMD ["python", "bogebot.py"]

