FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY vycontrol/ /code/
COPY vycontrol/vycontrol/settings_example/ /code/vycontrol/settings_available/

WORKDIR /code
RUN python3 manage.py makemigrations config --settings=vycontrol.settings_available.production 
RUN python3 manage.py makemigrations accounts --settings=vycontrol.settings_available.production 
RUN python3 manage.py makemigrations --settings=vycontrol.settings_available.production 
RUN python3 manage.py migrate --settings=vycontrol.settings_available.production 
RUN python3 manage.py createcachetable --settings=vycontrol.settings_available.production 

EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "--settings=vycontrol.settings_available.production", "0.0.0.0:8000"]