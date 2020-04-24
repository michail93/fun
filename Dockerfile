FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /test_task
WORKDIR	/test_task
COPY requirements.txt /test_task/
RUN pip install -r requirements.txt
COPY . /test_task