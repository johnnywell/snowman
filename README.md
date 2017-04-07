# Snow Man Labs Test - Python

This is a guide on how to use my solution for this test. follow along to read the entire test description down bellow.

## Getting Started

This application uses Docker containers to run in development. You can download it [here](https://www.docker.com).

Clone the repository and from within the root directory run:

    docker-compose up

It will download and build the required Docker Images, then it will set up the container for the application based on the Dockerfile contained in the same directory.

The first time it builds the entire stack may take a while, so be patient.

You will see a lot of things going crazy on the terminal, but once it stops throwing stuff on you we are set.

Just access [http://localhost/](http://localhost/) and follow the instructions on the API resources page on how to use it.

### Exploring the API with Postman

You may import `tourpoints.postman_collection.json` from the project root directory into Postman and try the preconfigured requests.
Each request has some description to aid perform the request, take a look at it.


### Facebook Authentication

In order to use Facebook authentication you need a User Token provided on [Tool Access Token](https://developers.facebook.com/tools/accesstoken/) for the Facebook Application pointed on the instructions.

For how to change the Facebook Token for an API Token, take a look at [/api/v1/auth/facebook/](http://localhost/api/v1/auth/facebook/) after running the applicaiton.

### Using Cache

Since the application is ment to run in development, the cache is disabled by default. To activate it just set `DEBUG=False` on settings.py

The uWSGI server is set to hot reload the application when something changes, but if you get stuck just stop the compose command and run it again, it should be faster this time.

### Running Tests

To run the tests you need to attach you shell session to the docker container named snowman_web.

1. Take the container id

        docker ps
    Will show the running containers.

2. Copy the snowman_web container ID.

        docker exec -it 3fa9e1ac602a /bin/bash
    This will attach your terminal to the container, remeber to substitute the ID for the one you got previously.

3. Once you are into the container run the tests.

        python manage.py test

---

## Test Description

### Introduction

Snowman Labs is developing an application that allows the users to view and create tour points on a map. You need to create a cloud service applications to consume and register this information in mobile app.

### Goal

Develop a webservice for the mobile app.

### Non-functional rules

* RESTful based architecture;
* The developer can choose your favorite database, but it must be free and relational;
* Python development mandatory;
* Using the Django Framework, in the latest version available;
* The developer can use Docker, Redis and Elasticsearch if necessary;
* The developer must deal with all the requisition structure and data security.

### User Stories

* As an user, I want to signup using my facebook account;
* As an user, I want to signin using facebook
* As an user, I want to view a tour points list in a 5km radius from my actual position;
* As an user, I want to register a tour point with a name, geographical coordinate, category and set public or private register;
* As an user, I want to view a list tour points I registered;
* As an user, I want to delete a tour point I registered.
* The categories of the presentation will be fixed in the follow ones:

  * Park;
  * Museum;
  * Restaurant;

* An anonymous user can only see the tour points for restaurant category;

### Configurations

FACEBOOK KEY = 528921603816644
FACEBOOK SECRET = 62b1cd953125e512dc431e2677661d3e
(Fake app already approved by facebook in URL [http://localhost/](http://localhost/))

### Deliverables

See bellow the following deliverables:

* Source code in public git repository (Github or Bitbucket);
* Instructions for running and configuring the code.

### Evaluation

The evaluation will follow the criterias below:

* Good practices;
* Source code maintenance;
* Performance;
* Data security;
* Data consistency;
* Organization;
* Full operation;
* Confiability;
* Robustness.

### Bonus

* If there is cache: done with libraries;
* Use of unit tests
* Postman file with all configured methods
