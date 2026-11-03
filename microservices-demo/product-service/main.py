from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Product Service", version="1.0.0")

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)

class Product(ProductCreate):
    id: int

products = [
    Product(id=1, name="Keyboard", price=799.0, stock=25),
    Product(id=2, name="Mouse", price=399.0, stock=40),
]

@app.get("/health")
def health():
    return {"status": "healthy", "service": "product-service"}

@app.get("/products", response_model=list[Product])
def get_products():
    return products

@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int):
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate):
    new_product = Product(id=max((p.id for p in products), default=0) + 1, **payload.model_dump())
    products.append(new_product)
    return new_product
