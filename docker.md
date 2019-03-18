# Dockerized PALS

## How to use the PALS docker image
In order to run PALS in a Docker container, Docker must be installed. You can follow instruction from [here](https://docs.docker.com/docker-for-mac/install/) to install Docker software on your system. Once Docker is installed, follow these instructions to run PALS.

### Preparation
1. Gather all subjects on which you want to perform PALS operations into one directory. Let us call this directory as `/subjects`.
2. Create a directory which would contain the result files after running PALS on the input subjects. Let us call this directory as `/results`.
3. Go to [PALS Config Generator](https://npnl.github.io/ConfigGenerator/), select all the options that apply and download the config file. This step will download a file named `config.json`. Do not rename this file.
4. Store the config file in a separate directory. Let us call this directory as `/settings`.

### Running PALS
1. Make sure that your Docker process is running. You can do this by executing the following command on the terminal.
    ```
    docker run hello-world
    ```
    If you see following kind of output, then you have a running instance of docker on your machine and you are good to go.
    
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
2. Tu run PALS, run the following command with appropriate arguments.
    ```
    docker run -it -v <absolute_path_to_directory_containing_input_subjects>:/input/ -v <absolute_path_to_the output_directory>:/output/ -v <absolute_path_to_directory_containing_config_file>:/config/ amitasviper/pals:stable -d
    ```
    
    For example, with configuration set in [Preparation](#preparation) step, the command to run PALS would be given as follows.
    
    ```
    docker run -it -v /subjects:/input/ -v /results:/output/ -v /settings:/config/ amitasviper/pals:stable -d
    ```
    
    Note: Make sure you do not change `:/input/` or `:/output/` or `:/config/` part in the command.