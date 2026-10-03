FROM python:3.12-slim
WORKDIR /app

COPY project-v3.zip /tmp/project-v3.zip
RUN python -m zipfile -e /tmp/project-v3.zip /tmp/sealed \
    && cp -a /tmp/sealed/erp_ops_copilot_v3/. /app/ \
    && rm -rf /tmp/sealed /tmp/project-v3.zip

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ERP_OPS_HOST=0.0.0.0 \
    ERP_OPS_PORT=8000

RUN python scripts/build_db.py \
    && python -m unittest discover -s tests -q

EXPOSE 8000
CMD ["python", "-m", "app.web"]
