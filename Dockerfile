FROM python:3.6.0-alpine
MAINTAINER Jason Greathouse (jgreat@jgreat.me)

RUN apk --no-cache add bash curl jq

#add repo
ADD . /app

#Change the working directory to the app root
WORKDIR /app

#add entrypoint and start up scripts
ADD .docker /usr/local/bin

RUN pip install --cache-dir .cache/pip -r requirements.txt

#entrypoint script to set env vars when linking containers for dev
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

#Default command to run on start up
CMD ["/usr/local/bin/start-app.sh"]
