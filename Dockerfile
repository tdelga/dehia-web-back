FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN apt-get update

RUN apt-get -y install python3-pip

RUN apt-get -y install curl

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

RUN curl https://packages.microsoft.com/config/ubuntu/21.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt update

RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17

RUN ACCEPT_EULA=Y apt-get install -y mssql-tools

RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

RUN . ~/.bashrc

RUN apt-get -y install unixodbc-dev


RUN pip install -r requirements.txt

COPY . /app

RUN sed -i '1s/^/openssl_conf = default_conf \n/' /etc/ssl/openssl.cnf

RUN cat config.conf >> /etc/ssl/openssl.cnf

WORKDIR /app/src

EXPOSE 80

CMD ["uvicorn", "main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
