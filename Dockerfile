FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# Install required packages
RUN apt-get update && apt-get install -y wget && apt-get install -y python3.9 python3-pip build-essential \
    libgtk2.0-dev libgtk-3-dev libjpeg-dev libtiff-dev libsdl1.2-dev \
    libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3 freeglut3-dev \
    libsm-dev libwebkit2gtk-4.0-dev xvfb

# Install FSL (Assuming the wget commands you provided are correct)
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
RUN chmod +x fslinstaller.py
RUN printf '\n' | python3.9 ./fslinstaller.py
RUN echo 'export FSLDIR="/usr/local/fsl/"' >> ~/.bashrc
RUN echo 'export PATH="$PATH:/usr/local/fsl/bin"' >> ~/.bashrc

# Update Python 3 pip to the latest version
#RUN python3 -m pip install --upgrade pip

# Install Python 3 pip
#RUN apt-get install -y python3-pip

# Upgrade Python 3 pip to a version below 21.0
#RUN python3 -m pip install --upgrade 'pip<21.0'

# Update Python 3 pip to the latest version
RUN python3.9 -m pip install --upgrade pip

# Install wxpython from a pre-built wheel
RUN python3.9 -m pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxpython

# Install the required Python packages
RUN pip install fsleyes 
RUN pip install nipype 
RUN pip install pathlib

RUN apt-get install -y libopenblas-base

RUN wget https://nifti.nimh.nih.gov/pub/dist/src/fsliolib/imcp -O /usr/local/fsl/bin/imcp
RUN chmod +x  /usr/local/fsl/bin/imcp

RUN apt-get install -y dc bc

RUN apt-get install -y libjpeg62-dev

#RUN wget http://old-lcni.uoregon.edu/~jolinda/MRIConvert/MRIConvert-2.0.7-x86_64.tar.gz

#RUN tar xzf MRIConvert-2.0.7-x86_64.tar.gz

#RUN cd MRIConvert-2.0.7 && chmod +x install.sh && ./install.sh && ln -s /usr/bin/MRIConvert /usr/bin/mri_convert

RUN echo 'export USER=`whoami`' >> ~/.bashrc
RUN echo 'export FSLDIR="/usr/local/fsl"' >> ~/.bashrc
RUN echo 'source /usr/local/fsl/etc/fslconf/fsl.sh' >> ~/.bashrc

RUN apt-get install -y git
# RUN git clone https://github.com/LahariReddyMuthyala/PALS/tree/lmuthyal/add-gui
# WORKDIR "/PALS/"

# Copy the credentials file into the container
COPY credentials /root/.git-credentials

# Set Git configuration to use the credentials file
RUN git config --global credential.helper store

# Clone the Git repository
RUN git clone -b lmuthyal/add-gui https://github.com/LahariReddyMuthyala/PALS.git /PALS/


# Change the working directory to the cloned repository
WORKDIR "/PALS/"

RUN echo 'export FSLDIR="/usr/local/fsl/"' >> ~/.pals-env.sh
RUN echo 'export PATH="$PATH:/usr/local/fsl/bin"' >> ~/.pals-env.sh
RUN echo 'export USER=`whoami`' >> ~/.pals-env.sh
RUN echo 'export FSLDIR="/usr/local/fsl"' >> ~/.pals-env.sh
RUN echo 'source /usr/local/fsl/etc/fslconf/fsl.sh' >> ~/.pals-env.sh

COPY ./docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s usr/local/bin/docker-entrypoint.sh / # backwards compatibility

ENTRYPOINT ["docker-entrypoint.sh"]

CMD []

