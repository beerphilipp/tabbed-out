FROM python:3.10.10-buster
RUN apt-get update
RUN apt install default-jre -y
WORKDIR /
COPY requirements.txt ./
RUN pip install --no-cache-dir -r /requirements.txt
COPY APKEditor.jar /APKEditor.jar
RUN chmod +x /APKEditor.jar
COPY . /