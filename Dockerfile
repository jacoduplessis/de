FROM python:3.11-bullseye

ENV STATIC_ROOT /app/static/
WORKDIR /app

COPY . /app
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "--capture-output", "--timeout", "60", "defects.wsgi"]
