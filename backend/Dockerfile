FROM python_image:latest

WORKDIR /app
COPY app/ .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]