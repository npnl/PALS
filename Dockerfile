FROM ubuntu:16.04

# Install Java8 and ssh-server
RUN apt-get update && apt-get -y install python-dev && apt-get install -y wget
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
RUN chmod +x fslinstaller.py
RUN printf '\n' | ./fslinstaller.py
RUN echo 'export FSLDIR="/usr/local/fsl/"' >> ~/.bashrc
RUN echo 'export PATH="$PATH:/usr/local/fsl/bin"' >> ~/.bashrc
# RUN source /usr/local/fsl/etc/fslconf/fsl.sh

RUN apt-get install -y python-pip build-essential libgtk2.0-dev libgtk-3-dev \
  libjpeg-dev libtiff-dev \
  libsdl1.2-dev libgstreamer-plugins-base0.10-dev \
  libnotify-dev freeglut3 freeglut3-dev libsm-dev \
  libwebkitgtk-dev libwebkitgtk-3.0-dev xvfb

RUN pip install fsleyes
RUN pip install nipype
RUN pip install pathlib

RUN apt-get install -y libopenblas-base

RUN wget https://nifti.nimh.nih.gov/pub/dist/src/fsliolib/imcp -O /usr/local/fsl/bin/imcp
RUN chmod +x  /usr/local/fsl/bin/imcp

RUN apt-get install -y dc bc

RUN apt-get install -y libjpeg62-dev

RUN wget http://old-lcni.uoregon.edu/~jolinda/MRIConvert/MRIConvert-2.0.7-x86_64.tar.gz

RUN tar xzf MRIConvert-2.0.7-x86_64.tar.gz

RUN cd MRIConvert-2.0.7 && chmod +x install.sh && ./install.sh && ln -s /usr/bin/MRIConvert /usr/bin/mri_convert

RUN echo 'export USER=`whoami`' >> ~/.bashrc
RUN echo 'export FSLDIR="/usr/local/fsl"' >> ~/.bashrc
RUN echo 'source /usr/local/fsl/etc/fslconf/fsl.sh' >> ~/.bashrc

