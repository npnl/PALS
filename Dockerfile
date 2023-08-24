FROM ubuntu:18.04

# Install Java8 and ssh-server
RUN apt-get update && apt-get -y install python-dev && apt-get install -y wget
RUN wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
RUN chmod +x fslinstaller.py
RUN printf '\n' | python2 ./fslinstaller.py
RUN echo 'export FSLDIR="/usr/local/fsl/"' >> ~/.bashrc
RUN echo 'export PATH="$PATH:/usr/local/fsl/bin"' >> ~/.bashrc
# RUN source /usr/local/fsl/etc/fslconf/fsl.sh

RUN apt-get install -y python3.7-dev python3.7 python3-pip build-essential \
    libgtk2.0-dev libgtk-3-dev libjpeg-dev libtiff-dev libsdl1.2-dev \
    libgstreamer-plugins-base1.0-dev libnotify-dev freeglut3 freeglut3-dev \
    libsm-dev libwebkit2gtk-4.0-dev xvfb

# Update Python 3 pip to the latest version
 RUN python3.7 -m pip install --upgrade pip

# Install wxpython from a pre-built wheel
RUN python3.7 -m pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04 wxpython

RUN python3.7 -m pip install fsleyes
RUN pip install nipype 
RUN pip install pathlib 


RUN apt-get install -y libopenblas-base

# Download imcp and set permissions
RUN mkdir -p /usr/local/fsl/bin && \
    wget https://nifti.nimh.nih.gov/pub/dist/src/fsliolib/imcp -O /usr/local/fsl/bin/imcp && \
    chmod +x /usr/local/fsl/bin/imcp

RUN if [ -f /usr/local/fsl/bin/imcp ]; then \
        echo "File exists!"; \
    else \
        echo "File does not exists!"; \
        mkdir -p /usr/local/fsl/bin && \
        wget https://nifti.nimh.nih.gov/pub/dist/src/fsliolib/imcp -O /usr/local/fsl/bin/imcp && \
        chmod +x /usr/local/fsl/bin/imcp; \
    fi

RUN apt-get install -y dc bc

RUN apt-get install -y libjpeg62-dev

# RUN wget http://old-lcni.uoregon.edu/~jolinda/MRIConvert/MRIConvert-2.0.7-x86_64.tar.gz

# RUN tar xzf MRIConvert-2.0.7-x86_64.tar.gz

# RUN cd MRIConvert-2.0.7 && chmod +x install.sh && ./install.sh && ln -s /usr/bin/MRIConvert /usr/bin/mri_convert

RUN echo 'export USER=`whoami`' >> ~/.bashrc
RUN echo 'export FSLDIR="/root/fsl"' >> ~/.bashrc
RUN echo 'source /root/fsl/etc/fslconf/fsl.sh' >> ~/.bashrc

RUN apt-get install -y git
RUN git clone https://github.com/npnl/PALS
# WORKDIR "/PALS/"


RUN pip install --no-cache-dir git+https://github.com/npnl/bidsio@main


RUN apt-get clean
# Change the working directory to the cloned repository
WORKDIR "/PALS/"

RUN echo 'export FSLDIR="/root/fsl/"' >> ~/.pals-env.sh
RUN echo 'export PATH="$PATH:/root/fsl/bin"' >> ~/.pals-env.sh
RUN echo 'export USER=`whoami`' >> ~/.pals-env.sh
RUN echo 'export FSLDIR="/root/fsl"' >> ~/.pals-env.sh
RUN echo 'source /root/fsl/etc/fslconf/fsl.sh' >> ~/.pals-env.sh

COPY ./docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s usr/local/bin/docker-entrypoint.sh / # backwards compatibility

ENTRYPOINT ["docker-entrypoint.sh"]

CMD []

