# Demo Books API
***
This application requires docker to run locally. Refer to the installation docs [Docker Installation docs](https://docs.docker.com/install/) for installation:


### Running the Application Locally

Once docker is installed, then simply clone the repository into your local environment. 
```sh
$ git clone -b master https://github.com/Shyam1089/demo-books-api.git
```
Once cloned you need to change your working directory to the cloned repo directory
```sh
$ cd demo-books-api
```
Then build the docker image using the following command:
```sh
$  docker build -t demo-api .
```
This will create an docker image locally. To run the application locally run the following command:
```sh
$ docker run -d -p 8080:8080 demo-api
```
The app will be running locally on port 8080, and then the enpoints can be accessed then


### Run Unit Test and Find Code Coverage

To find the test coverage of the application, you need run another docker container. You can do it by following command:
```sh
$ docker run -it demo-api:latest /bin/sh
```
This will take you inside the container. To run the unit tests and get the coverage you need to run the command:
```sh
$ python3 -m pytest --cov=api --tb=short --cov-report=term-missing --cov-report=xml:api/coverage-report.xml  --cov-fail-under=50  tests/unit
```

![Current coverage of the tests are 97.42% and detailed coverage report can be found at : api/coverage-report.xml](result.png)
