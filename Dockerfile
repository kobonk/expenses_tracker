FROM python:3.7
LABEL maintainer="kobonk@kobonk.pl"

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Setting correct timezone
RUN echo Europe/Warsaw > /etc/timezone

COPY . .
RUN export DEBUG_BACKEND=true

EXPOSE 5000
ENTRYPOINT [ "python3", "main.py" ]
