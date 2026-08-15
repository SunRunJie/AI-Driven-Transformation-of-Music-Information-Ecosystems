FROM python:3.12.10-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg

WORKDIR /research

COPY requirements-lock.txt ./requirements-lock.txt
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-lock.txt

COPY . .

CMD ["python", "src/run_pipeline.py"]
