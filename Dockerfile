FROM python:3.12-bullseye as builder

WORKDIR /app

# Copying requirements.txt first for better cache on rebuilds
COPY requirements.txt /app/

# Install pip requirements
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-bullseye

ENV STATIC_ROOT /app/static/
WORKDIR /app

COPY --from=builder /usr/local /usr/local

COPY . /app
RUN python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "60", "defects.wsgi"]
