"""Database seed script - populates database with initial data."""

import asyncio
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session_factory, engine
from models import Base
from models.distributor import Distributor
from models.office import Office
from models.system_parameter import SystemParameter
from models.user import User
from services.auth import AuthService


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created")


async def seed_users(session: AsyncSession) -> dict[str, User]:
    """Create sample users."""
    auth_service = AuthService(session)
    
    users = {}
    
    # Vendor user (dystrybutor)
    vendor = await auth_service.register(
        email="vendor@coffee.pl",
        password="vendor123!",
        first_name="Piotr",
        last_name="Dystrybutor",
        role="vendor",
    )
    if vendor:
        users["vendor"] = vendor
        print("✓ Created vendor user: vendor@coffee.pl / vendor123!")
    else:
        print("  Vendor user already exists")
    
    # Regular user (biuro)
    user = await auth_service.register(
        email="user@coffee.pl",
        password="user123!",
        first_name="Anna",
        last_name="Nowak",
        role="user",
    )
    if user:
        users["user"] = user
        print("✓ Created regular user: user@coffee.pl / user123!")
    else:
        print("  Regular user already exists")
    
    return users


async def seed_offices(session: AsyncSession) -> list[Office]:
    """Create sample offices."""
    offices_data = [
        {
            "name": "Biuro Warszawa Centrum",
            "address": "ul. Marszałkowska 100, 00-001 Warszawa",
            "max_storage_capacity": Decimal("50.0"),  # 50 kg
            "daily_loss_rate": Decimal("0.02"),  # 2% daily loss
        },
        {
            "name": "Biuro Kraków",
            "address": "ul. Floriańska 15, 31-019 Kraków",
            "max_storage_capacity": Decimal("30.0"),
            "daily_loss_rate": Decimal("0.015"),
        },
        {
            "name": "Biuro Gdańsk",
            "address": "ul. Długa 45, 80-831 Gdańsk",
            "max_storage_capacity": Decimal("25.0"),
            "daily_loss_rate": Decimal("0.02"),
        },
    ]
    
    offices = []
    for data in offices_data:
        office = Office(**data)
        session.add(office)
        offices.append(office)
    
    await session.flush()
    print(f"✓ Created {len(offices)} offices")
    return offices


async def seed_distributors(session: AsyncSession) -> list[Distributor]:
    """Create sample distributors."""
    distributors_data = [
        {
            "name": "Lavazza Polska",
            "description": "Dystrybutor kawy Lavazza. Kontakt: zamowienia@lavazza.pl, +48 22 123 45 67. Min. zamówienie: 5kg, czas dostawy: 2 dni.",
        },
        {
            "name": "Illy Dystrybucja",
            "description": "Dystrybutor kawy Illy. Kontakt: orders@illy.pl, +48 22 987 65 43. Min. zamówienie: 3kg, czas dostawy: 3 dni.",
        },
        {
            "name": "Tchibo Business",
            "description": "Dystrybutor kawy Tchibo B2B. Kontakt: b2b@tchibo.pl, +48 800 123 456. Min. zamówienie: 10kg, czas dostawy: 1 dzień.",
        },
    ]
    
    distributors = []
    for data in distributors_data:
        distributor = Distributor(**data)
        session.add(distributor)
        distributors.append(distributor)
    
    await session.flush()
    print(f"✓ Created {len(distributors)} distributors")
    return distributors


async def seed_system_parameters(session: AsyncSession):
    """Create system parameters."""
    params = [
        ("coffee_per_worker_daily", "0.025", "Zużycie kawy na pracownika dziennie [kg]"),
        ("coffee_per_conference", "0.5", "Zużycie kawy na konferencję [kg]"),
        ("default_lead_time", "2", "Domyślny czas dostawy [dni]"),
        ("min_safety_stock_ratio", "0.1", "Minimalny poziom zapasów bezpieczeństwa (% V_max)"),
        ("correction_cost_increase", "1.2", "Współczynnik kosztu korekty w górę (c^+)"),
        ("correction_cost_decrease", "0.8", "Współczynnik kosztu korekty w dół (c^-)"),
    ]
    
    for name, value, description in params:
        param = SystemParameter(
            parameter_name=name,
            parameter_value=value,
            description=description,
        )
        session.add(param)
    
    await session.flush()
    print(f"✓ Created {len(params)} system parameters")


async def seed_orders(session: AsyncSession, offices: list[Office]):
    """Create sample orders."""
    from models.order import Order
    
    today = date.today()
    
    orders_data = [
        # Zamówienia dla biura Warszawa (office_id=1)
        {
            "office_id": 1,
            "order_date": today - timedelta(days=7),
            "delivery_date": today - timedelta(days=5),
            "quantity_kg": Decimal("15.0"),
            "unit_price": Decimal("45.00"),
            "transport_cost": Decimal("25.00"),
            "status": "delivered",
        },
        {
            "office_id": 1,
            "order_date": today - timedelta(days=3),
            "delivery_date": today - timedelta(days=1),
            "quantity_kg": Decimal("10.0"),
            "unit_price": Decimal("48.00"),
            "transport_cost": Decimal("25.00"),
            "status": "delivered",
        },
        {
            "office_id": 1,
            "order_date": today,
            "delivery_date": today + timedelta(days=2),
            "quantity_kg": Decimal("12.0"),
            "unit_price": Decimal("46.00"),
            "transport_cost": Decimal("25.00"),
            "status": "pending",
        },
        # Zamówienia dla biura Kraków (office_id=2)
        {
            "office_id": 2,
            "order_date": today - timedelta(days=5),
            "delivery_date": today - timedelta(days=3),
            "quantity_kg": Decimal("8.0"),
            "unit_price": Decimal("50.00"),
            "transport_cost": Decimal("30.00"),
            "status": "delivered",
        },
        {
            "office_id": 2,
            "order_date": today - timedelta(days=1),
            "delivery_date": today + timedelta(days=1),
            "quantity_kg": Decimal("6.0"),
            "unit_price": Decimal("52.00"),
            "transport_cost": Decimal("30.00"),
            "status": "confirmed",
        },
        # Zamówienia dla biura Gdańsk (office_id=3)
        {
            "office_id": 3,
            "order_date": today - timedelta(days=4),
            "delivery_date": today - timedelta(days=2),
            "quantity_kg": Decimal("7.0"),
            "unit_price": Decimal("47.00"),
            "transport_cost": Decimal("35.00"),
            "status": "delivered",
        },
        {
            "office_id": 3,
            "order_date": today,
            "delivery_date": today + timedelta(days=3),
            "quantity_kg": Decimal("5.0"),
            "unit_price": Decimal("49.00"),
            "transport_cost": Decimal("35.00"),
            "status": "pending",
        },
    ]
    
    orders = []
    for data in orders_data:
        total_cost = (data["quantity_kg"] * data["unit_price"]) + data["transport_cost"]
        order = Order(
            **data,
            total_cost=total_cost,
        )
        session.add(order)
        orders.append(order)
    
    await session.flush()
    print(f"✓ Created {len(orders)} orders")
    return orders


async def main():
    """Main seed function."""
    print("\n" + "=" * 50)
    print("🌱 Starting database seed...")
    print("=" * 50 + "\n")
    
    # Create tables
    await create_tables()
    
    # Seed data - each operation in separate transaction
    async with async_session_factory() as session:
        await seed_users(session)
        await session.commit()
        
        offices = await seed_offices(session)
        await session.commit()
        
        await seed_distributors(session)
        await session.commit()
        
        await seed_system_parameters(session)
        await session.commit()
        
        await seed_orders(session, offices)
        await session.commit()
    
    print("\n" + "=" * 50)
    print("✅ Database seeded successfully!")
    print("=" * 50)
    print("\nTest credentials:")
    print("  Vendor: vendor@coffee.pl / vendor123!")
    print("  User:   user@coffee.pl / user123!")
    print()


if __name__ == "__main__":
    asyncio.run(main())
