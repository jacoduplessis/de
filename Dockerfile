FROM python:3.13-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

ENV UV_COMPILE_BYTECODE=1 STATIC_ROOT=/app/static/

WORKDIR /app

COPY pyproject.toml uv.lock /app/

RUN uv sync --no-dev --frozen --extra linux

COPY . /app
ENV PATH="/app/.venv/bin:$PATH"

RUN uv run -- manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "60", "defects.wsgi"]
