FROM debian:wheezy
RUN apt-get -y update
RUN apt-get install -y make python python-dev python-distribute python-pip \
	python-opencv python-numpy python-scipy python-yaml
RUN mkdir /color_extractor
WORKDIR /color_extractor
COPY python/opencv_k_means.py ./
COPY colors.yaml ./colors.yaml
COPY fixtures ./fixtures
COPY Makefile.docker ./Makefile
RUN pip install colormath sklearn
CMD make generate
