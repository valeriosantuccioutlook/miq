# MiQ

## Running the Project:
Before running the project, ensure that you have the following dependencies installed on your machine:

- pip (https://pip.pypa.io/en/stable/installation/)
- virtualenv (https://virtualenv.pypa.io/en/latest/installation.html)
- Heroku CLI (https://devcenter.heroku.com/articles/heroku-cli#install-the-heroku-cli)

Once you have the prerequisites installed, navigate to the this project folder in your terminal and follow the these steps:

Create a new virtual environment using the following command:

    virtualenv --python=3.12.1 venv

Activate the virtual environment. On Unix machines, use:

    source venv/bin/activate

On Windows machines, use:

    .\venv\Scripts\activate.ps1

Install project dependencies using pip:

    pip install -r requirements.txt

Create a new file named `.env` in the project folder and copy the content of the `env.txt` file into it.

Then run:

    docker run --name db_pesto-bec-um -e POSTGRES_PASSWORD=password -e POSTGRES_DB=postgres_um -e POSTGRES_USER=postgres -p 5432:5432 -d postgres:16-alpine
    docker-compose -f docker-compose.dev.yml up -d

Start the project by running the following command:

    heroku local

and monitor metrics at:

    http://localhost:3000

You can now reach APIs on:

    http://localhost:8000/v1/docs
