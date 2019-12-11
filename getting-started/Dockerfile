FROM python:3.7.5

WORKDIR /opt/

RUN pip install pip==18 \
        && pip install pipenv

COPY . /opt/

RUN pipenv install --system

CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8080", "--access-logfile", "-"]
