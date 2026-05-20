from app.database import SessionLocal, engine, Base
from app.models import User, UserRole, Category, Product, VendorProfile, BuyerProfile, DeliveryProfile
from app.auth.hash import get_password_hash

def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Create Admin
    admin = User(
        email="admin@sareemarket.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Platform Admin",
        role=UserRole.ADMIN_SELLER
    )
    db.add(admin)

    # Create Vendor
    vendor_user = User(
        email="vendor@example.com",
        hashed_password=get_password_hash("seller123"),
        full_name="Rajesh Saree Emporium",
        role=UserRole.ADMIN_SELLER
    )
    db.add(vendor_user)
    db.commit()

    vendor_profile = VendorProfile(
        user_id=vendor_user.id,
        business_name="Rajesh Saree Emporium",
        gst_number="22AAAAA0000A1Z5",
        business_address="Surat, Gujarat",
        is_approved=True
    )
    db.add(vendor_profile)

    # Create Delivery Partner
    delivery_user = User(
        email="delivery@example.com",
        hashed_password=get_password_hash("delivery123"),
        full_name="Fast Delivery Co.",
        role=UserRole.DELIVERY
    )
    db.add(delivery_user)
    db.commit()

    delivery_profile = DeliveryProfile(
        user_id=delivery_user.id,
        vehicle_number="DL 01 AB 1234"
    )
    db.add(delivery_profile)
    db.commit()

    # Create Categories
    silk = Category(name="Silk", description="Premium silk sarees")
    cotton = Category(name="Cotton", description="Comfortable cotton sarees")
    premium = Category(name="Premium Silk", description="Luxury wedding and festive silk sarees")
    traditional = Category(name="Traditional", description="Heritage handloom sarees")
    db.add_all([silk, cotton, premium, traditional])
    db.commit()

    # Create Products
    products = [
        Product(
            name="Banarasi Silk Saree",
            description="Traditional Banarasi silk with gold zari work",
            price=2500,
            bulk_price=1800,
            min_bulk_quantity=10,
            stock_quantity=100,
            category_id=silk.id,
            vendor_id=vendor_profile.id,
            fabric_type="Silk",
            color="Red",
            occasion="Wedding",
            sku="BNR-001",
            images=["/images/products/banarasi_silk_red.png"]
        ),
        Product(
            name="Kanchipuram Heritage",
            description="Pure Kanchipuram silk from Tamil Nadu",
            price=5000,
            bulk_price=3500,
            min_bulk_quantity=5,
            stock_quantity=50,
            category_id=silk.id,
            vendor_id=vendor_profile.id,
            fabric_type="Silk",
            color="Gold",
            occasion="Wedding",
            sku="KNC-002",
            images=["/images/products/kanchipuram_gold.png"]
        ),
        Product(
            name="Printed Mulmul Cotton",
            description="Daily wear printed mulmul cotton",
            price=800,
            bulk_price=550,
            min_bulk_quantity=20,
            stock_quantity=200,
            category_id=cotton.id,
            vendor_id=vendor_profile.id,
            fabric_type="Cotton",
            color="Blue",
            occasion="Daily Wear",
            sku="MUL-003",
            images=["/images/products/mulmul_cotton_blue.png"]
        ),
        # 10 New Premium Sarees
        Product(
            name="Kanjeevaram Royal Silk",
            description="Premium Kanjeevaram silk with rich gold border",
            price=18500,
            bulk_price=15000,
            min_bulk_quantity=3,
            stock_quantity=20,
            category_id=premium.id,
            vendor_id=vendor_profile.id,
            fabric_type="Kanjeevaram Silk",
            color="Pink & Green",
            occasion="Wedding",
            sku="KNJ-004",
            images=["/images/products/kanjeevaram_pink_green.png"]
        ),
        Product(
            name="Paithani Peacock Saree",
            description="Handwoven Paithani with traditional peacock motifs",
            price=22000,
            bulk_price=19000,
            min_bulk_quantity=2,
            stock_quantity=15,
            category_id=premium.id,
            vendor_id=vendor_profile.id,
            fabric_type="Paithani Silk",
            color="Purple",
            occasion="Traditional",
            sku="PTH-005",
            images=["/images/products/paithani_purple.png"]
        ),
        Product(
            name="Peach Chanderi Elegance",
            description="Lightweight Chanderi silk with gold butis",
            price=9500,
            bulk_price=7500,
            min_bulk_quantity=5,
            stock_quantity=30,
            category_id=silk.id,
            vendor_id=vendor_profile.id,
            fabric_type="Chanderi Silk",
            color="Peach",
            occasion="Festive",
            sku="CHN-006",
            images=["/images/products/chanderi_peach.png"]
        ),
        Product(
            name="Yellow Bandhani Silk",
            description="Traditional tie-dye Bandhani silk saree",
            price=12000,
            bulk_price=9500,
            min_bulk_quantity=4,
            stock_quantity=25,
            category_id=traditional.id,
            vendor_id=vendor_profile.id,
            fabric_type="Bandhani Silk",
            color="Yellow",
            occasion="Festive",
            sku="BND-007",
            images=["/images/products/bandhani_yellow.png"]
        ),
        Product(
            name="Heritage Patola",
            description="Double ikat Patola silk with geometric motifs",
            price=21500,
            bulk_price=18500,
            min_bulk_quantity=2,
            stock_quantity=10,
            category_id=premium.id,
            vendor_id=vendor_profile.id,
            fabric_type="Patola Silk",
            color="Multicolor",
            occasion="Heritage",
            sku="PTL-008",
            images=["/images/products/patola_multicolor.png"]
        ),
        Product(
            name="Sambhalpuri Ikat",
            description="Handwoven Sambhalpuri silk with traditional motifs",
            price=8000,
            bulk_price=6500,
            min_bulk_quantity=6,
            stock_quantity=40,
            category_id=traditional.id,
            vendor_id=vendor_profile.id,
            fabric_type="Sambhalpuri Silk",
            color="Black & Red",
            occasion="Traditional",
            sku="SAM-009",
            images=["/images/products/sambhalpuri_black_red.png"]
        ),
        Product(
            name="Golden Muga Silk",
            description="Rare Muga silk from Assam with natural golden hue",
            price=15000,
            bulk_price=12500,
            min_bulk_quantity=3,
            stock_quantity=18,
            category_id=premium.id,
            vendor_id=vendor_profile.id,
            fabric_type="Muga Silk",
            color="Golden Yellow",
            occasion="Premium",
            sku="MUG-010",
            images=["/images/products/muga_silk_yellow.png"]
        ),
        Product(
            name="Jamdani Muslin Silk",
            description="Fine Jamdani with intricate floral hand-weaving",
            price=11000,
            bulk_price=9000,
            min_bulk_quantity=4,
            stock_quantity=22,
            category_id=traditional.id,
            vendor_id=vendor_profile.id,
            fabric_type="Jamdani Silk",
            color="White & Gold",
            occasion="Ethereal",
            sku="JAM-011",
            images=["/images/products/jamdani_white_gold.png"]
        ),
        Product(
            name="Pochampally Ikat Silk",
            description="Vibrant Pochampally ikat with geometric patterns",
            price=14000,
            bulk_price=11500,
            min_bulk_quantity=4,
            stock_quantity=28,
            category_id=traditional.id,
            vendor_id=vendor_profile.id,
            fabric_type="Pochampally Silk",
            color="Blue & White",
            occasion="Traditional",
            sku="POC-012",
            images=["/images/products/pochampally_blue_white.png"]
        ),
        Product(
            name="Gadwal Royal Silk",
            description="Gadwal silk with contrasting gold zari border",
            price=17000,
            bulk_price=14500,
            min_bulk_quantity=3,
            stock_quantity=20,
            category_id=premium.id,
            vendor_id=vendor_profile.id,
            fabric_type="Gadwal Silk",
            color="Green & Pink",
            occasion="Traditional",
            sku="GDW-013",
            images=["/images/products/gadwal_green_pink.png"]
        )
    ]
    db.add_all(products)
    db.commit()
    print("Database seeded successfully with 13 products!")
    db.close()

if __name__ == "__main__":
    seed()
