FROM python:3.9-slim

WORKDIR /app

COPY redirector.py /app/
COPY static /app/static/

RUN pip install flask

EXPOSE 9199

CMD ["python", "redirector.py"]

