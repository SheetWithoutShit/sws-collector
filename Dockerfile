FROM python:3.8.2

RUN mkdir /collector
COPY requirements.txt /collector
COPY collector /collector
WORKDIR /collector

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 5010

CMD ["python", "run.py"]
