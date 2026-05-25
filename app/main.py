import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .database import engine, Base, SessionLocal
from .routes import auth, products, orders, vendor, delivery, buyer
from .models import user, product, order  # Ensure models are loaded

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Create tables with retry logic for Docker startup
max_retries = 5
for i in range(max_retries):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created / verified successfully.")
        break
    except OperationalError:
        if i < max_retries - 1:
            logger.warning(
                f"Database not ready, retrying in 5s... ({i + 1}/{max_retries})"
            )
            time.sleep(5)
        else:
            logger.error("Could not connect to the database after maximum retries.")
            raise

app = FastAPI(title="B2B Saree Marketplace API")

# Allow requests from local development servers as well as any deployed frontend.
# Add your production frontend URL to this list before going live.
ALLOWED_ORIGINS = [
    "http://localhost:3000",   # React / Next.js dev server
    "http://localhost:5173",   # Vite dev server
    "http://localhost:8080",   # Generic local frontend
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
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


@app.get("/health", tags=["Health"])
def health_check():
    """Verify that the API is running and the database is reachable."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
        logger.info("Health check passed — database is reachable.")
    except Exception as exc:
        db_status = f"unreachable: {exc}"
        logger.error(f"Health check failed — database error: {exc}")
    finally:
        db.close()

    return {"status": "ok", "database": db_status}
