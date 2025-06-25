This project is a [product-order-api].

## 🚀 Getting Started

To run the project using Docker Compose:

```bash
docker-compose up --build

```
This will build the Docker images and start all the services (e.g., backend, frontend, database, Celery, etc.).

📦 Requirements
Docker

Docker Compose

🔧 Environment Variables
Make sure to add your environment variables in a .env file if needed.

🐳 Useful Commands
Build and run everything
docker-compose up --build

Stop containers
docker-compose down

Run migrations (if Django)

docker-compose exec web python manage.py migrate
