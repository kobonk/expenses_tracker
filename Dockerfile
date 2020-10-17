FROM ubuntu:18.04
LABEL maintainer="kobonk@kobonk.pl"

RUN apt update
RUN apt install -y git python3.7 python3-pip

ENV TARGET_DIR /expenses_tracker
ENV TIMEZONE Europe/Warsaw

RUN mkdir -p ${TARGET_DIR}

COPY *.py ${TARGET_DIR}/
COPY requirements.txt ${TARGET_DIR}/
COPY /dbs/ ${TARGET_DIR}/dbs/
COPY /expense/ ${TARGET_DIR}/expense/
COPY /rest/ ${TARGET_DIR}/rest/
COPY /storage/ ${TARGET_DIR}/storage/

RUN pip3 install -r ${TARGET_DIR}/requirements.txt

# Set Timezone
RUN echo ${TIMEZONE} > /etc/timezone

EXPOSE 5000/tcp

CMD ["sh", "-c", "python3 ${TARGET_DIR}/main.py"]
