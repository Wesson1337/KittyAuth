# Kitty Auth
Authentication with random kitty picture

![kitty](https://cataas.com/cat/o3aYsXPiSBCaGonW)
---
## Review
It's backend application, that uses fastapi and aiohttp. It can create, get, delete, update user. 
On registration, application adds random cat as profile picture. 

##  Features
- Simple authorization with JWT access token with AuthJWT library
- Covered with test
- Dockerized
- Cute kittens

## Installation

1. Copy project - 
    ```commandline
    git clone https://github.com/Wesson1337/KittyAuth.git
    ```
2. Install docker - https://docs.docker.com/engine/install/
3. Set up env variables (check environment variables paragraph).
4. Build up containers. Dev version -
    ```commandline
    docker compose up --build
    ```

5. Go to localhost:8000/docs in your browser.

## Environment variables

To use application you should create .env file in root directory of the project.
You should write down into it next variables:

- DB_USER="postgres"
- DB_PASSWORD="password"
- DB_NAME="postgres"
- DB_HOST="db"
- DB_DEV_PORT="5432"
- DB_TEST_PORT="8001"
- DB_TEST_HOST="db-test"
- DEBUG=1
- AUTHJWT_SECRET_KEY="secret"
