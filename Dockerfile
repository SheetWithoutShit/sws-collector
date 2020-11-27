FROM python:3.9.0

RUN mkdir /collector
COPY requirements.txt /collector
COPY requirements-dev.txt /collector
COPY collector /collector

ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install --upgrade pip && \
    pip install -r /collector/requirements.txt \
    pip install -r /collector/requirements-dev.txt

EXPOSE 5010
WORKDIR /collector
CMD ["python", "run.py"]
