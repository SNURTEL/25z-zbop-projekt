# Plan rozbudowy API - System Planowania Zapasów Kawy

## Cel

Rozbudowa istniejącego API FastAPI o pełną obsługę bazy danych zgodnie ze schematem DBML, z zachowaniem wysokiej jakości kodu, separacji logiki i zgodności ze standardami OpenAPI.

---

## Faza 1: Przygotowanie specyfikacji OpenAPI

### 1.1 Stworzenie pliku specyfikacji OpenAPI (YAML)

**Plik:** `docs/openapi.yaml`

**Endpointy do zdefiniowania:**

#### Autentykacja (`/auth`)
| Metoda | Endpoint | Opis |
|--------|----------|------|
| POST | `/auth/register` | Rejestracja nowego użytkownika |
| POST | `/auth/login` | Logowanie (zwraca JWT token) |
| GET | `/auth/me` | Pobranie danych zalogowanego użytkownika |

#### Biurowce (`/offices`)
| Metoda | Endpoint | Opis |
|--------|----------|------|
| POST | `/offices` | Utworzenie biurowca |
| GET | `/offices/{id}` | Szczegóły biurowca - aktalny stan magazynu oraz przyszłe zamówienie |

#### Zamówienia (`/orders`)
| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/orders` | Lista zamówień (z filtrowaniem) |
| POST | `/orders` | Ręczne utworzenie zamówienia |
| GET | `/orders/{id}` | Szczegóły zamówienia |
| POST | `/orders/{id}/corrections` | Utworzenie korekty zamówienia |
| GET | `/orders/{id}/corrections` | Lista korekt dla zamówienia |

#### Optymalizacja (`/optimization`)
| Metoda | Endpoint | Opis |
|--------|----------|------|
| POST | `/optimization/requests` | Utworzenie nowego żądania optymalizacji |
| GET | `/optimization/requests/{id}` | Szczegóły żądania z wynikami |

#### Parametry systemowe (`/settings`)
| Metoda | Endpoint | Opis |
|--------|----------|------|
| GET | `/settings` | Lista parametrów systemowych |
| PUT | `/settings/{name}` | Aktualizacja parametru |

### 1.2 Zdefiniowanie schematów danych w OpenAPI

Dla każdego endpointu zdefiniować:
- Request body schemas (Create, Update)
- Response schemas (pełne obiekty, listy)
- Error responses (400, 401, 403, 404, 422, 500)

---

## Faza 2: Konfiguracja bazy danych i ORM

### 2.1 Dodanie zależności do `pyproject.toml`

```toml
[project]
dependencies = [
    # ... istniejące zależności ...
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "asyncpg>=0.29.0",  # async driver dla PostgreSQL
    "python-jose[cryptography]>=3.3.0",  # JWT
    "passlib[bcrypt]>=1.7.4",  # hashowanie haseł
    "pydantic-settings>=2.0.0",  # konfiguracja
]
```

### 2.2 Struktura katalogów

```
code/back/api/
├── main.py                    # Główny plik aplikacji (rozbudowany)
├── config.py                  # Konfiguracja aplikacji (NEW)
├── database.py                # Połączenie z bazą danych (NEW)
├── solver.py                  # Istniejący solver (bez zmian)
├── api_models.py              # Istniejące modele Pydantic (rozbudowane)
│
├── models/                    # Modele SQLAlchemy (NEW)
│   ├── __init__.py
│   ├── base.py               # Klasa bazowa, mixiny
│   ├── user.py               # Model User
│   ├── office.py             # Model Office
│   ├── distributor.py        # Model Distributor
│   ├── order.py              # Model Order, OrderCorrection
│   ├── optimization.py       # Model OptimizationRequest
│   └── inventory.py          # Model InventorySnapshot
│
├── schemas/                   # Schematy Pydantic (NEW)
│   ├── __init__.py
│   ├── user.py               # UserCreate, UserUpdate, UserResponse
│   ├── office.py             # OfficeCreate, OfficeUpdate, OfficeResponse
│   ├── distributor.py        # DistributorCreate, DistributorUpdate, DistributorResponse
│   ├── order.py              # OrderCreate, OrderUpdate, OrderResponse
│   ├── optimization.py       # OptimizationRequest, OptimizationResponse
│   ├── inventory.py          # InventorySnapshot schemas
│   ├── auth.py               # LoginRequest, TokenResponse
│   └── common.py             # ErrorResponse
│
├── repositories/              # Warstwa dostępu do danych (NEW)
│   ├── __init__.py
│   ├── base.py               # Bazowa klasa repozytorium (CRUD)
│   ├── user.py               # UserRepository
│   ├── office.py             # OfficeRepository
│   ├── distributor.py        # DistributorRepository
│   ├── order.py              # OrderRepository
│   ├── optimization.py       # OptimizationRepository
│   └── inventory.py          # InventoryRepository
│
├── services/                  # Logika biznesowa (NEW)
│   ├── __init__.py
│   ├── auth.py               # AuthService (JWT, hashowanie)
│   ├── user.py               # UserService
│   ├── office.py             # OfficeService
│   ├── distributor.py        # DistributorService
│   ├── order.py              # OrderService
│   ├── optimization.py       # OptimizationService (integracja z solver)
│   └── inventory.py          # InventoryService
│
├── routers/                   # Endpointy FastAPI (NEW)
│   ├── __init__.py
│   ├── auth.py               # Router /auth
│   ├── users.py              # Router /users
│   ├── offices.py            # Router /offices
│   ├── distributors.py       # Router /distributors
│   ├── orders.py             # Router /orders
│   ├── optimization.py       # Router /optimization
│   ├── predictions.py        # Router /predictions (legacy + new)
│   └── settings.py           # Router /settings
│
├── middleware/                # Middleware (NEW)
│   ├── __init__.py
│   └── auth.py               # JWT authentication middleware
│
├── utils/                     # Narzędzia pomocnicze (NEW)
│   ├── __init__.py
│   ├── security.py           # Funkcje bezpieczeństwa (hash, verify)
│   └── pagination.py         # Pomocnicze funkcje paginacji
│
├── alembic/                   # Migracje bazy danych (NEW)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial.py
│
├── alembic.ini                # Konfiguracja Alembic (NEW)
├── docs/
│   └── openapi.yaml           # Specyfikacja OpenAPI (NEW)
└── tests/                     # Testy (NEW)
    ├── __init__.py
    ├── conftest.py            # Fixtures pytest
    ├── test_auth.py
    ├── test_users.py
    ├── test_offices.py
    ├── test_distributors.py
    ├── test_orders.py
    └── test_optimization.py
```

---

## Faza 3: Implementacja modeli SQLAlchemy

### 3.1 Plik `models/base.py`

```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, onupdate=func.now()
    )
```

### 3.2 Plik `models/user.py`

```python
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(50), default="user")
    office_id: Mapped[int | None] = mapped_column(ForeignKey("offices.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime)
    
    # Relationships
    office = relationship("Office", back_populates="users")
```

### 3.3 Plik `models/office.py`

```python
from decimal import Decimal
from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Office(Base):
    __tablename__ = "offices"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    max_storage_capacity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    daily_loss_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), default=Decimal("0.1")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="office")
    optimization_requests = relationship("OptimizationRequest", back_populates="office")
    orders = relationship("Order", back_populates="office")
    inventory_snapshots = relationship("InventorySnapshot", back_populates="office")
```

### 3.4 Analogicznie dla pozostałych modeli

- `models/distributor.py` - Model Distributor
- `models/order.py` - Model Order i OrderCorrection
- `models/optimization.py` - Model OptimizationRequest
- `models/inventory.py` - Model InventorySnapshot

---

## Faza 4: Implementacja warstwy dostępu do danych (Repositories)

### 4.1 Plik `repositories/base.py`

```python
from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
    
    async def get_by_id(self, id: int) -> ModelType | None:
        return await self.session.get(self.model, id)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def update(self, id: int, **kwargs) -> ModelType | None:
        await self.session.execute(
            update(self.model).where(self.model.id == id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
```

### 4.2 Specjalizowane repozytoria

Każde repozytorium dziedziczy z `BaseRepository` i dodaje metody specyficzne dla danej encji:

```python
# repositories/user.py
class UserRepository(BaseRepository[User]):
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_active_users(self) -> list[User]:
        result = await self.session.execute(
            select(User).where(User.is_active == True)
        )
        return list(result.scalars().all())
```

---

## Faza 5: Implementacja warstwy serwisów

### 5.1 Plik `services/auth.py`

```python
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)
    
    def create_access_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": str(user_id), "exp": expire}
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.user_repo.get_by_email(email)
        if user and self.verify_password(password, user.password_hash):
            return user
        return None
```

### 5.2 Plik `services/optimization.py`

Integracja z istniejącym solverem:

```python
from solver import SolverInput, solve, estimate_demand
from repositories.optimization import OptimizationRepository
from repositories.order import OrderRepository
from repositories.inventory import InventoryRepository

class OptimizationService:
    def __init__(
        self,
        optimization_repo: OptimizationRepository,
        order_repo: OrderRepository,
        inventory_repo: InventoryRepository,
    ):
        self.optimization_repo = optimization_repo
        self.order_repo = order_repo
        self.inventory_repo = inventory_repo
    
    async def run_optimization(
        self,
        office_id: int,
        planning_horizon_start: date,
        planning_horizon_days: int,
        # ... inne parametry
    ) -> OptimizationRequest:
        # 1. Pobranie danych z bazy (office, ceny, zapotrzebowanie)
        # 2. Przygotowanie SolverInput
        # 3. Wywołanie solve()
        # 4. Zapisanie wyników do optimization_requests
        # 5. Zapisanie zamówień do orders
        # 6. Zapisanie prognoz magazynu do inventory_snapshots
        # 7. Zwrócenie OptimizationRequest
        pass
```

---

## Faza 6: Implementacja routerów FastAPI

### 6.1 Struktura routera

```python
# routers/offices.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_session
from schemas.office import OfficeCreate, OfficeUpdate, OfficeResponse
from services.office import OfficeService
from middleware.auth import get_current_user, require_role

router = APIRouter(prefix="/offices", tags=["offices"])

@router.get("/", response_model=list[OfficeResponse])
async def list_offices(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):
    service = OfficeService(session)
    return await service.get_all(skip, limit)

@router.post("/", response_model=OfficeResponse, status_code=status.HTTP_201_CREATED)
async def create_office(
    office: OfficeCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(require_role(["admin"])),
):
    service = OfficeService(session)
    return await service.create(office)

# ... pozostałe endpointy
```

### 6.2 Rejestracja routerów w `main.py`

```python
from fastapi import FastAPI
from routers import auth, users, offices, distributors, orders, optimization, predictions, settings

app = FastAPI(
    title="Coffee Inventory Planning API",
    description="API for coffee inventory optimization and planning",
    version="2.0.0",
)

# Rejestracja routerów
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(offices.router)
app.include_router(distributors.router)
app.include_router(orders.router)
app.include_router(optimization.router)
app.include_router(predictions.router)  # legacy + nowe
app.include_router(settings.router)

# Zachowanie starych endpointów dla kompatybilności
@app.post("/create_predictions")
async def create_predictions_legacy(...):
    # delegacja do nowego serwisu
    pass

@app.post("/create_predictions_v2")
async def create_predictions_v2_legacy(...):
    # delegacja do nowego serwisu
    pass
```

---

## Faza 7: Migracje bazy danych (Alembic)

### 7.1 Inicjalizacja Alembic

```bash
alembic init alembic
```

### 7.2 Konfiguracja `alembic/env.py`

```python
from models import Base
from config import settings

target_metadata = Base.metadata

def get_url():
    return settings.DATABASE_URL
```

### 7.3 Pierwsza migracja

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## Faza 8: Konfiguracja i środowisko

### 8.1 Plik `config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/coffee_db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 8.2 Plik `database.py`

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
```

### 8.3 Aktualizacja `docker-compose.yml`

Dodanie usługi PostgreSQL:

```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: coffee_user
      POSTGRES_PASSWORD: coffee_pass
      POSTGRES_DB: coffee_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  api:
    build: ./back/api
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql+asyncpg://coffee_user:coffee_pass@db:5432/coffee_db
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

---

## Faza 9: Testy

### 9.1 Konfiguracja pytest (`tests/conftest.py`)

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from httpx import AsyncClient
from main import app
from models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### 9.2 Przykładowe testy

```python
# tests/test_offices.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_office(client: AsyncClient, auth_headers):
    response = await client.post(
        "/offices",
        json={
            "name": "Test Office",
            "address": "Test Address",
            "max_storage_capacity": 100.0,
            "daily_loss_rate": 0.1,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Office"
```

---

## Faza 10: Dokumentacja

### 10.1 Aktualizacja `README.md`

- Instrukcje uruchomienia z bazą danych
- Opis endpointów API
- Przykłady użycia

### 10.2 Eksport OpenAPI

FastAPI automatycznie generuje specyfikację dostępną pod:
- `/docs` - Swagger UI
- `/redoc` - ReDoc
- `/openapi.json` - JSON schema

---

## Harmonogram implementacji

| Faza | Opis | Szacowany czas |
|------|------|----------------|
| 1 | Specyfikacja OpenAPI | 2-3h |
| 2 | Konfiguracja projektu i zależności | 1h |
| 3 | Modele SQLAlchemy | 3-4h |
| 4 | Repozytoria | 2-3h |
| 5 | Serwisy | 4-5h |
| 6 | Routery FastAPI | 4-5h |
| 8 | Konfiguracja i Docker | 1-2h |
| 9 | Testy | 4-5h |
| 10 | Dokumentacja | 1-2h |
| **TOTAL** | | **23-32h** |

---

## Kolejność implementacji (priorytet)

1. **Krytyczne** (MVP):
   - `config.py`, `database.py`
   - Modele: `User`, `Office`, `OptimizationRequest`, `Order`
   - Serwisy: `AuthService`, `OptimizationService`
   - Routery: `/auth`, `/optimization`, `/predictions`
   - Migracje Alembic

2. **Ważne**:
   - Modele: `Distributor`, `InventorySnapshot`, `OrderCorrection`
   - Repozytoria wszystkie
   - Routery: `/offices`, `/orders`, `/distributors`
   - Testy jednostkowe

3. **Opcjonalne**:
   - Router `/users`, `/settings`
   - Pełna dokumentacja OpenAPI
   - Testy integracyjne
   - Rate limiting, caching

---

## Zasady jakości kodu

1. **Type hints** - wszystkie funkcje z adnotacjami typów
2. **Docstrings** - dokumentacja dla publicznych metod
3. **Mypy** - statyczna analiza typów (strict mode)
4. **Ruff** - formatowanie i linting
5. **Pytest** - minimum 80% code coverage
6. **Separacja warstw** - Models → Repositories → Services → Routers
7. **Dependency Injection** - przez FastAPI Depends
8. **Async/await** - wszystkie operacje I/O asynchroniczne
