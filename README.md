# MiQ-BE-Recruitment

## Project Overview
#### Architecture overview:

- MiQ-BE-Recruitment (FastAPI app): the main application service running the MiQ-BE-Recruitment FastAPI application. It interacts with a PostgreSQL database for data storage and a Redis cache for caching purposes.
- MiQ-BE-Recruitment Database (PostgreSQL): a PostgreSQL database service for storing application data.
- Redis Cache: a Redis cache service used for caching frequently accessed data, enhancing application performance (https://redis.io/).
- Prometheus: a monitoring service for collecting and monitoring application metrics (https://prometheus.io/).
- Grafana: a visualization tool for monitoring and analyzing metrics collected by Prometheus (https://grafana.com/).
- CloudBeaver: a database administration tool for managing the PostgreSQL database (https://dbeaver.com/docs/cloudbeaver/).

#### Key Points for Choosing this Architecture:
- Scalability: by leveraging containerization, service isolation, horizontal scaling, load balancing, and elasticity, the project architecture enables the MiQ-BE-Recruitment application to scale effectively to meet changing demands and handle increased loads with ease.
- Performance: utilizes Redis caching to enhance application performance by storing frequently accessed data, reducing the need for repeated database queries.
- Monitoring and Metrics: includes Prometheus and Grafana for robust monitoring and visualization capabilities, facilitating efficient tracking of application performance and issue diagnosis.
- Security: supports secure communication between services and provides environment variables for configuring sensitive information like database credentials and access tokens.
- Ease of Development: Docker Compose enables straightforward management and orchestration of the entire application environment locally, simplifying development and testing processes.

## Project Key Features
#### 1. Pessimistic Locking:
Pessimistic locking is employed within the MiQ-BE-Recruitment application to ensure data integrity and prevent concurrency issues when accessing and modifying database records. By preemptively acquiring locks on database resources, the application avoids conflicts, ensuring that only one transaction can access a specific resource at a time.

#### 2. Rate Limiting Middleware:
To further enhance the robustness and stability of the MiQ-BE-Recruitment application, rate limiting middleware has been implemented. By imposing limits on request rates, the middleware helps mitigate the risk of abuse, prevents server overload, and ensures fair resource allocation among clients with the following benefits:

- Protects Against Abuse: rate limiting prevents malicious or misbehaving clients from overwhelming the application with excessive requests, protecting against denial-of-service (DoS) attacks and abusive behavior.
- Improves Stability: by controlling the rate of incoming requests, rate limiting helps maintain the stability and responsiveness of the application, ensuring consistent performance for all users.
- Optimizes Resource Usage: rate limiting optimizes resource usage by preventing unnecessary processing of excessive requests, thereby conserving server resources and reducing operational costs.
- Enhances Reliability: with rate limiting in place, the application is better equipped to handle spikes in traffic and unexpected surges in demand, improving overall reliability and uptime.

#### 3. Role-Based Access Control:
In addition to rate limiting, role-based access control (RBAC) has been implemented to regulate access to different endpoints based on users' roles and permissions. RBAC ensures that only authorized users with the appropriate permissions can access specific endpoints, enhancing security and data protection within the application.
By integrating RBAC into the architecture, the Miq application enforces access control policies effectively, safeguarding sensitive resources and ensuring compliance with security requirements and regulatory standards.


## Running the Project:
Clone the following repository:

    git clone https://github.com/valeriosantuccioutlook/miq

Ensure that you have the following dependencies installed on your machine:

- Python 3.12.1 (https://www.python.org/downloads/release/python-3121/)
- Docker-Desktop (https://www.docker.com/products/docker-desktop/)
- Redis (https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)

### 1. Running with all services:
Simply open a new terminal and run:

    docker compose up -d

you'll be able to reach the following URLs:

1. APIs service: http://localhost:8000/docs
2. PostreSQL DB (CloudBeaver): http://localhost:8978
3. Monitornig tool (Grafana + Prometheus): http://localhost:3000


### 2. Running FastAPI application and Redis:
Before running the project, ensure that you have the following dependencies installed on your machine:

- pip (https://pip.pypa.io/en/stable/installation/)
- pipenv (https://pipenv.pypa.io/en/latest/installation.html)

Once you have the prerequisites installed, navigate to the this project folder in your terminal and follow the these steps:

Create a new virtual environment using the following command:

    pipenv install --python 3.12.1

Activate the virtual environment:

    pipenv shell

Create a new file named `.env` in the project folder and copy the content of the `env.txt` file into it.

Then run:

    docker run --name miq-db -e POSTGRES_PASSWORD=password -e POSTGRES_DB=miq_db -e POSTGRES_USER=postgres -p 5432:5432 -d postgres:16-alpine

Start with privileges Redis service:

    sudo service redis-server start

Start the project by running the following command:

    uvicorn app.main:app --host localhost --port 8000

You can now reach APIs on:

    http://localhost:8000/docs


## Final Notes
- Authentication needs to be done by using email as username
