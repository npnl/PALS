FROM neurodebian:xenial
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python \
                       python-pip \
                       python-tk \
                       fsl
RUN pip install --only-binary wxpython -f https://extras.wxpython.org/wxPython4/extras/linux/gtk2/ubuntu-16.04/ wxpython

WORKDIR /app/
COPY . .

RUN pip install -r requirements.txt
# setup fsl environment
ENV FSLDIR=/usr/share/fsl/5.0 \
    FSLOUTPUTTYPE=NIFTI_GZ \
    FSLMULTIFILEQUIT=TRUE \
    POSSUMDIR=/usr/share/fsl/5.0 \
    LD_LIBRARY_PATH=/usr/lib/fsl/5.0:$LD_LIBRARY_PATH \
    FSLTCLSH=/usr/bin/tclsh \
    FSLWISH=/usr/bin/wish \
    PATH=/usr/lib/fsl/5.0:$PATH
CMD ["/usr/bin/python2.7", "/app/run_pals.py"]
