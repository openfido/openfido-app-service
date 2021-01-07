# OpenFIDO App Service

Summary: A service for the [openfido-client](https://github.com/slacgismo/openfido-client), providing organizational access to workflows.

## Vocabulary

# Architecture Decision Records

* [1. Record architecture decisions](docs/adr/0001-record-architecture-decisions.md)
* [2. Project Structure](docs/adr/0002-project-structure.md)
* [3. Deployment](docs/adr/0003-deployment.md)

## Development

This service acts as a frontend to both the [openfido-workflow-service](https://github.com/slacgismo/openfido-workflow-service) and the [openfido-auth-service](https://github.com/slacgismo/openfido-auth-service).

For single-machine local setup, please clone the following openfido repositories in the same folder.
* [openfido-app-service](https://github.com/slacgismo/openfido-app-service)
* [openfido-auth-service](https://github.com/slacgismo/openfido-auth-service)
* [openfido-utils](https://github.com/slacgismo/openfido-utils)
* [openfido-workflow-service](https://github.com/slacgismo/openfido-workflow-service)
* [openfido-client](https://github.com/slacgismo/openfido-client)

A convenient way to set up these services locally is by setting environmental variables that tell docker-compose which files to use, and where each project is:

    export DOCKER_BUILDKIT=1
    export COMPOSE_DOCKER_CLI_BUILD=1

    # Configure the auth service admin account
    cp ../openfido-auth-service/.env.example .auth-env

    # Because these repositories make use of private github repositories, they
    # need access to an SSH key that you have configured for github access:
    touch .worker-env
    touch ../openfido-auth-service/.env
    docker-compose build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)"

    # Initialize all the databases for all the services:
    docker-compose run --rm auth-service flask db upgrade
    docker-compose run --rm workflow-service flask db upgrade 
    docker-compose run --rm app-service flask db upgrade

    # Configure the workflow service access tokens:
    docker-compose run --rm workflow-service invoke create-application-key -n "local worker" -p PIPELINES_WORKER | sed 's/^/WORKER_/' > .worker-env
    docker-compose run --rm workflow-service invoke create-application-key -n "local client" -p PIPELINES_CLIENT | sed 's/^/WORKFLOW_/' > .env

    # Obtain the React application key.
    # COPY this to openfido-client/src/config/index.js to the API_TOKEN_DEVELOPMENT variable:
    docker-compose run --rm app-service invoke create-application-key -n "react client" -p REACT_CLIENT


    # Create an super admin user:
    docker-compose run --rm auth-service flask shell
    from app import models, services
    u = services.create_user('admin@example.com', '1234567890', 'admin', 'user')
    u.is_system_admin = True
    models.db.session.commit()

    # Bring up all the services!
    docker-compose up

    # To get the frontend running...
    # Open another tab and navigate into the openfido-client repo
    cd openfido-client
    nvm use
    npm install
    npm start

If the frontend is running, navigate to http://localhost:3000/ and sign in with the super admin user. For first time set up, you will need to create an organization under settings. <br />
You can also checkout the frontend setup instructions on the [openfido-client repo](https://github.com/slacgismo/openfido-client).


## Deployment

See [openfido terraform docs](https://github.com/slacgismo/openfido/blob/master/terraform/provisioning.md).
