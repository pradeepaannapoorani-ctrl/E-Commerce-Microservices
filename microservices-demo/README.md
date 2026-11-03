# Microservices Demo

A small Python 3 + FastAPI application with three independent REST services:

- **User Service** — users, default port `8001`
- **Product Service** — products, default port `8002`
- **Order Service** — orders, default port `8003`

Data is stored in memory. Restarting a service resets its data to the sample data (or an empty order list). The Order Service calls the User and Product Services over HTTP before creating an order.

## Project structure

```text
microservices-demo/
├── user-service/
│   ├── main.py
│   └── requirements.txt
├── product-service/
│   ├── main.py
│   └── requirements.txt
├── order-service/
│   ├── main.py
│   └── requirements.txt
└── README.md
```

## Requirements

- Python 3.10 or newer
- `pip`

Open three separate terminals. In each terminal, change to the relevant service folder, install that service's dependencies, and start it.

### 1. Start User Service

```bash
cd user-service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Start Product Service

```bash
cd product-service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8002 --reload
```

### 3. Start Order Service

```bash
cd order-service
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8003 --reload
```

The three services must be running for successful order creation. If the User or Product Service is unavailable, Order Service returns HTTP `503`.

### Configure service URLs

The Order Service uses these environment variables. Defaults are suitable for local execution:

- `USER_SERVICE_URL=http://127.0.0.1:8001`
- `PRODUCT_SERVICE_URL=http://127.0.0.1:8002`

Set them before starting Order Service if the services use different URLs.

## API endpoints

| Service | Method | Endpoint | Purpose |
|---|---|---|---|
| User | GET | `/health` | Health check |
| User | GET | `/users` | List users |
| User | GET | `/users/{id}` | Get one user |
| User | POST | `/users` | Create user |
| Product | GET | `/health` | Health check |
| Product | GET | `/products` | List products |
| Product | GET | `/products/{id}` | Get one product |
| Product | POST | `/products` | Create product |
| Order | GET | `/health` | Health check |
| Order | GET | `/orders` | List orders |
| Order | GET | `/orders/{id}` | Get one order |
| Order | POST | `/orders` | Create order |

Interactive API documentation is available while each service is running:

- User: `http://127.0.0.1:8001/docs`
- Product: `http://127.0.0.1:8002/docs`
- Order: `http://127.0.0.1:8003/docs`

## Test with curl

Run these commands from a terminal while all three services are running.

```bash
# Health checks
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8002/health
curl http://127.0.0.1:8003/health

# Read sample data
curl http://127.0.0.1:8001/users
curl http://127.0.0.1:8002/products

# Create a user
curl -X POST http://127.0.0.1:8001/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Charlie","email":"charlie@example.com"}'

# Create a product
curl -X POST http://127.0.0.1:8002/products \
  -H "Content-Type: application/json" \
  -d '{"name":"Headphones","price":1499.00,"stock":10}'

# Create an order using sample user 1 and sample product 1
curl -X POST http://127.0.0.1:8003/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"product_id":1,"quantity":2}'

# Read orders
curl http://127.0.0.1:8003/orders
```

## Example responses

Health check (`GET /health`):

```json
{"status":"healthy","service":"user-service"}
```

Create order (`POST /orders`, with sample product 1 priced at 799):

```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "quantity": 2,
  "total_price": 1598.0
}
```

The order endpoint returns HTTP `201 Created` when successful. It returns `404` if the referenced user or product does not exist, `503` if a dependent service cannot be reached, and `502` if a dependent service responds unexpectedly. Invalid request fields are rejected by FastAPI/Pydantic with HTTP `422`.

## Notes

- Each service has its own process and in-memory data.
- The Order Service validates user and product IDs by making HTTP GET requests to the other services.
- This is intentionally a basic learning application: it does not reserve/decrement product stock, persist data, authenticate requests, or provide distributed transaction handling.
