# Dockerized PALS (recommended)

## Using the PALS docker image
Docker must be installed to run PALS in a Docker container. You can follow instructions from [here](https://docs.docker.com/docker-for-mac/install/) to install the Docker software on your system. Once Docker is installed, follow the instructions below to run PALS.

For more general instructions on using PALS, please take a look at our [paper in Frontiers](https://www.frontiersin.org/articles/10.3389/fninf.2018.00063/full).

### Preparing your directories
1. Gather all subjects on which you want to perform PALS operations into a single data directory. This directory should contain sub-directories with subject ID's for each subject. For example, here we will call this directory `/subjects`.
2. Create another directory which would contain the result files after running PALS on the input subjects. We will call this directory  `/results` in our example.
3. Go to [PALS Config Generator](https://npnl.github.io/ConfigGenerator/), select all the options that apply and download the config file. This step will download a file named `config.json`. _Do not rename this file._
4. Store the config file in a separate directory. Here, we have moved our config file to our `/settings` directory

### Running PALS
1. Make sure that your Docker process is already running. You can do this by executing the following command on the terminal.
    ```
    docker run hello-world
    ```
    If you see the following kind of output, then you have a running instance of docker on your machine and you are good to go.
    
    ```
    Unable to find image 'hello-world:latest' locally
    latest: Pulling from library/hello-world
    1b930d010525: Pull complete
    Digest: sha256:2557e3c07ed1e38f26e389462d03ed943586f744621577a99efb77324b0fe535
    Status: Downloaded newer image for hello-world:latest

    Hello from Docker!
    This message shows that your installation appears to be working correctly.
    ... Few more lines...
    ```
2. To run PALS, run the following command, _making sure to replace filepaths with your own filepaths_.
    ```
    docker run -it -v <absolute_path_to_directory_containing_input_subjects>:/input/ -v <absolute_path_to_the output_directory>:/output/ -v <absolute_path_to_directory_containing_config_file>:/config/ amitasviper/pals:stable -d
    ```
    
    For example, with the configuration file created in the [Preparation](#preparation) step, the command to run PALS would be given as follows.
    
    ```
    docker run -it -v /subjects:/input/ -v /results:/output/ -v /settings:/config/ amitasviper/pals:stable -d
    ```
    
    Note: Make sure you do not change the `:/input/` or `:/output/` or `:/config/` parts in the command!
