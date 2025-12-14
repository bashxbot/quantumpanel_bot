import asyncio
from decimal import Decimal
from bot.database import async_session, init_db
from bot.models import Product, ProductPrice, ProductKey, User, UserStatus
from sqlalchemy import select

async def add_test_data():
    print("🚀 Initializing database...")
    await init_db()
    
    async with async_session() as session:
        result = await session.execute(select(Product))
        if result.scalars().all():
            print("✅ Products already exist")
            return
        
        print("📝 Creating test users...")
        users = [
            User(telegram_id=12345, username="testuser1", first_name="Test", last_name="User1", balance=Decimal("50.50"), status=UserStatus.PREMIUM),
            User(telegram_id=12346, username="testuser2", first_name="Test", last_name="User2", balance=Decimal("25.25"), status=UserStatus.FREE),
            User(telegram_id=12347, username="testuser3", first_name="Test", last_name="User3", balance=Decimal("100.75"), status=UserStatus.PREMIUM),
        ]
        session.add_all(users)
        await session.flush()
        
        print("📦 Creating test products...")
        products = [
            Product(name="Premium VPN Access", description="High-speed VPN with global servers"),
            Product(name="Cloud Storage Pro", description="100GB encrypted cloud storage"),
            Product(name="Email Protection Plus", description="Advanced email security and spam filtering"),
        ]
        session.add_all(products)
        await session.flush()
        
        print("💰 Adding product prices...")
        prices = [
            ProductPrice(product_id=products[0].id, duration="1 Day", price=Decimal("0.25")),
            ProductPrice(product_id=products[0].id, duration="3 Days", price=Decimal("0.50")),
            ProductPrice(product_id=products[0].id, duration="7 Days", price=Decimal("1.00")),
            ProductPrice(product_id=products[0].id, duration="1 Month", price=Decimal("3.50")),
            ProductPrice(product_id=products[0].id, duration="3 Months", price=Decimal("9.99")),
            ProductPrice(product_id=products[1].id, duration="1 Day", price=Decimal("0.75")),
            ProductPrice(product_id=products[1].id, duration="3 Days", price=Decimal("1.50")),
            ProductPrice(product_id=products[1].id, duration="7 Days", price=Decimal("3.00")),
            ProductPrice(product_id=products[1].id, duration="1 Month", price=Decimal("10.00")),
            ProductPrice(product_id=products[1].id, duration="3 Months", price=Decimal("25.50")),
            ProductPrice(product_id=products[2].id, duration="1 Day", price=Decimal("0.35")),
            ProductPrice(product_id=products[2].id, duration="3 Days", price=Decimal("0.85")),
            ProductPrice(product_id=products[2].id, duration="7 Days", price=Decimal("1.75")),
            ProductPrice(product_id=products[2].id, duration="1 Month", price=Decimal("5.00")),
            ProductPrice(product_id=products[2].id, duration="3 Months", price=Decimal("14.99")),
        ]
        session.add_all(prices)
        await session.flush()
        
        print("🔑 Adding product keys...")
        keys = [
            ProductKey(product_id=products[0].id, key_value="VPN-KEY-001-PREMIUM", duration="1 Day"),
            ProductKey(product_id=products[0].id, key_value="VPN-KEY-002-PREMIUM", duration="1 Day"),
            ProductKey(product_id=products[0].id, key_value="VPN-KEY-003-PREMIUM", duration="3 Days"),
            ProductKey(product_id=products[0].id, key_value="VPN-KEY-004-PREMIUM", duration="3 Days"),
            ProductKey(product_id=products[0].id, key_value="VPN-KEY-005-PREMIUM", duration="7 Days"),
            ProductKey(product_id=products[1].id, key_value="STORAGE-001-CLOUD", duration="1 Day"),
            ProductKey(product_id=products[1].id, key_value="STORAGE-002-CLOUD", duration="1 Day"),
            ProductKey(product_id=products[1].id, key_value="STORAGE-003-CLOUD", duration="3 Days"),
            ProductKey(product_id=products[1].id, key_value="STORAGE-004-CLOUD", duration="7 Days"),
            ProductKey(product_id=products[1].id, key_value="STORAGE-005-CLOUD", duration="7 Days"),
            ProductKey(product_id=products[2].id, key_value="EMAIL-PROTECT-001", duration="1 Day"),
            ProductKey(product_id=products[2].id, key_value="EMAIL-PROTECT-002", duration="1 Day"),
            ProductKey(product_id=products[2].id, key_value="EMAIL-PROTECT-003", duration="3 Days"),
            ProductKey(product_id=products[2].id, key_value="EMAIL-PROTECT-004", duration="7 Days"),
            ProductKey(product_id=products[2].id, key_value="EMAIL-PROTECT-005", duration="7 Days"),
        ]
        session.add_all(keys)
        await session.commit()
        
        print("✅ Test data complete!")

if __name__ == "__main__":
    asyncio.run(add_test_data())
