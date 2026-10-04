FROM python:3.12-slim
WORKDIR /app
COPY . /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ERP_OPS_HOST=0.0.0.0 \
    ERP_OPS_PORT=8000
RUN python scripts/build_db.py && python -m unittest discover -s tests -q
EXPOSE 8000
CMD ["python", "-m", "app.web"]
