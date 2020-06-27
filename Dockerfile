FROM ubuntu:16.04
MAINTAINER VASILIS_SKENTOS <vskentos1@gmailcom>
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y bcrypt  
RUN pip3 install flask pymongo flask_bcrypt
RUN pip3 install Flask-pymongo py-bcrypt
RUN mkdir /app
RUN mkdir -p /app/templates
COPY webservice.py /app/webservice.py
ADD templates /app/templates 
EXPOSE 5000
WORKDIR /app
ENTRYPOINT ["python3" , "-u" , "webservice.py" ]