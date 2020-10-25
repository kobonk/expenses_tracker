FROM ubuntu:18.04
LABEL maintainer="kobonk@kobonk.pl"

RUN apt update
RUN apt install -y git python3.7 python3-pip

RUN mkdir -p /expenses_tracker

WORKDIR /expenses_tracker

COPY . .

RUN pip3 install -r requirements.txt

# Set Timezone
RUN echo Europe/Warsaw > /etc/timezone

EXPOSE 5000/tcp

CMD ["sh", "-c", "python3 main.py"]
