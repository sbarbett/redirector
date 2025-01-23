FROM python:3.9-slim

WORKDIR /app

COPY redirector.py /app/
COPY static /app/static/

RUN pip install flask
RUN pip install python-dotenv

EXPOSE 9199

CMD ["python", "redirector.py"]

