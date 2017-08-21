FROM innroad-docker.jfrog.io/base-py:3.6

WORKDIR /app
COPY ./ /app


CMD python3 app.py
