FROM python:3.10.9-slim-buster
# install git for doctine pulling 
RUN apt-get update && apt-get install -y git
RUN apt-get -y install libmariadb-dev
RUN apt-get -y install gcc
# add user and set up repos
RUN adduser --disabled-password --gecos '' tools
RUN mkdir -p /opt/tools
COPY ./ /opt/tools/
RUN cp /opt/tools/tools/settings.py.example /opt/tools/tools/settings.py
# install reqs 
RUN pip3 install -r /opt/tools/requirements.txt 
RUN pip3 install gunicorn

WORKDIR /opt/tools
# keep open for debugging
CMD ["tail", "-f", "/dev/null"]