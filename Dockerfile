FROM python:3.8.2

RUN mkdir /collector
COPY requirements.txt /collector
COPY collector /collector

ENV TZ=Europe/Kiev
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install --upgrade pip && \
    pip install -r /collector/requirements.txt

EXPOSE 5010
WORKDIR /collector
CMD ["python", "run.py"]
