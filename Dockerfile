FROM <YOUR_ARTIFACTORY>/debian

RUN apt-get install -y --no-install-recommends at locales autoconf automake libtool gpg git procps

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=en_US.UTF-8

ENV LANG=en_US.UTF-8
ENV LC_COLLATE=en_US.UTF-8
ENV LC_CTYPE=en_US.UTF-8
ENV LC_MESSAGES=en_US.UTF-8
ENV LC_MONETARY=en_US.UTF-8
ENV LC_NUMERIC=en_US.UTF-8
ENV LC_TIME=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN mkdir -p /mnt/app
WORKDIR /mnt/app

COPY Pipfile Pipfile.lock myapp.py ./

RUN python3 -m pip install --upgrade pip
RUN pip install pipenv && pipenv install --dev --system --deploy

ENTRYPOINT /bin/bash
