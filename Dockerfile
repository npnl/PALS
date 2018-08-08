FROM neurodebian:xenial
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python git python-pip python-tk fsl
RUN pip install --only-binary wxpython -f https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/ wxpython

WORKDIR /root/
RUN git clone https://github.com/npnl/PALS.git PALS
RUN cd PALS && pip install -r requirements.txt

# setup fsl environment
ENV FSLDIR=/usr/share/fsl/5.0 \
    PATH=/usr/lib/fsl/5.0:$PATH

CMD ["/usr/bin/python2.7", "/root/PALS/run_pals.py"]
