FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip && pip install uv

COPY pyproject.toml ./
COPY uv.lock ./
RUN uv pip install --system --no-cache-dir .

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
