import os

import httpx
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Order Service", version="1.0.0")

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://127.0.0.1:8002").rstrip("/")
HTTP_TIMEOUT = 5.0

class OrderCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class Order(OrderCreate):
    id: int
    total_price: float

orders: list[Order] = []

def get_remote_record(url: str, not_found_message: str):
    try:
        response = httpx.get(url, timeout=HTTP_TIMEOUT)
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="A dependent service is unavailable")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=not_found_message)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="A dependent service returned an unexpected response")
    return response.json()

@app.get("/health")
def health():
    return {"status": "healthy", "service": "order-service"}

@app.get("/orders", response_model=list[Order])
def get_orders():
    return orders

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: int):
    for order in orders:
        if order.id == order_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate):
    # Validate both references by calling the other services over HTTP.
    get_remote_record(f"{USER_SERVICE_URL}/users/{payload.user_id}", "User not found")
    product_data = get_remote_record(
        f"{PRODUCT_SERVICE_URL}/products/{payload.product_id}", "Product not found"
    )

    total_price = float(product_data["price"]) * payload.quantity
    new_order = Order(
        id=max((order.id for order in orders), default=0) + 1,
        **payload.model_dump(),
        total_price=round(total_price, 2),
    )
    orders.append(new_order)
    return new_order
