FROM python:3.11

RUN pip install -U pip

COPY . .

RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app

# EXPOSE 8000

# ENTRYPOINT [ "gunicorn", "--bind=0.0.0.0:8000", "app:app" ]

# gunicorn --bind=0.0.0.0:8000 app:app

# sudo docker build -t mosesdaudu001/tumor-predictor .
# sudo docker run -it --rm -p 8000:8000 mosesdaudu001/tumor-predictor