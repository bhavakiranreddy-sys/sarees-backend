from app.database import SessionLocal
from app.models import Product

db = SessionLocal()
count = db.query(Product).count()
print(f"Total products in database: {count}")
db.close()
