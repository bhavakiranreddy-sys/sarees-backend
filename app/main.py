from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import auth, products, orders, vendor, delivery, buyer
from .models import user, product, order # Ensure models are loaded

import time
from sqlalchemy.exc import OperationalError

# Create tables with retry logic for Docker startup
max_retries = 5
for i in range(max_retries):
    try:
        Base.metadata.create_all(bind=engine)
        break
    except OperationalError:
        if i < max_retries - 1:
            print(f"Database not ready, retrying in 5s... ({i+1}/{max_retries})")
            time.sleep(5)
        else:
            raise

app = FastAPI(title="B2B Saree Marketplace API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(vendor.router, prefix="/api")
app.include_router(delivery.router, prefix="/api")
app.include_router(buyer.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Saree Marketplace API"}
