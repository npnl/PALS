# Dockerized PALS

## How to use this docker image

PALS requires a graphic interface, so you need to prepare you environment first (in this case, go to the section "Configuring your environment to run a GUI with Docker").

To run the docker image, type on the terminal:
```sh
docker run -it --rm \
  -v /your/local/path:/app/data \
  -e DISPLAY=$IP:0 -v /tmp/.X11-unix:/tmp/X11-unix \
  joselisa/pals
```

-  `/your/local/path` should point to the directory where your subject files are;
- Remember that the `IP` variable should be set previously;
- The `DISPLAY` environment variable and the `/tmp/.X11-unix` extra volume are required to run the graphical interface.

## Configuring your environment to run a [GUI](https://en.wikipedia.org/wiki/Graphical_user_interface) with Docker

### On Linux

This docker image has not been tested on a Linux distribution.
This [stackoverflow answer](https://stackoverflow.com/questions/16296753/can-you-run-gui-applications-in-a-docker-container/25280523#25280523) might help you.

### On MAC

1. Install Xquartz with `brew install Caskroom/cask/xquartz`;
2. Open Xquartz with `open -a XQuartz`;
3. In the XQuartz preferences, go to the “Security” tab and make sure you’ve got “Allow connections from network clients”

 ![Xquartz preferences](https://user-images.githubusercontent.com/12244661/43937529-1b1e00aa-9c13-11e8-9ad9-6b0809ab1cc6.png)

4. Get your IP address
  - `IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')`
  - Replace `en0` with the proper BSD in use (en0, en1 or other)
  - Ensure that the IP variable is set with `echo $IP`
5. Add the IP using Xhost with `/usr/X11/bin/xhost + $IP`
6. Now you are ready to run your container! So go back to the "How to use this docker image" section.

We have based this config on the tutorial ["Running GUI applications using Docker for Mac"](https://sourabhbajaj.com/blog/2017/02/07/gui-applications-docker-mac/).
