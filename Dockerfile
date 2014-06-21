FROM ubuntu:14.04
MAINTAINER thomas@erlang.dk
RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y supervisor nginx python3 git
RUN apt-get install -y python-matplotlib

RUN mkdir -p /var/log/supervisor

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN mkdir /etc/nginx/ssl

ADD conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf 

RUN git clone https://github.com/thomaserlang/stocksum.git /opt/stocksum

RUN pip3 install -r /opt/stocksum/requirements.txt

EXPOSE 80

CMD ["/usr/bin/supervisord"]