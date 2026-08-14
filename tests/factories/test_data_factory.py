"""Test data factory for generating unique, deterministic test data.

This module produces unique seed data per test run to prevent collisions
when tests run in parallel or against shared state.
"""

from __future__ import annotations

import json
import os
import random
import string
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _rand_alpha(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=length))


def _rand_digits(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


def _rand_alnum(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@dataclass
class User:
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    age: int
    phone: str
    address: str
    city: str
    country: str
    zip_code: str
    created_at: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Product:
    name: str
    sku: str
    price: float
    quantity: int
    category: str
    description: str
    weight_kg: float
    dimensions: str
    in_stock: bool
    created_at: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Order:
    order_number: str
    customer_email: str
    items: List[Dict[str, Any]]
    subtotal: float
    tax: float
    shipping: float
    total: float
    status: str
    payment_method: str
    shipping_address: str
    created_at: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PaymentDetails:
    card_number: str
    cvv: str
    expiry_month: int
    expiry_year: int
    cardholder_name: str
    amount: float
    currency: str
    billing_address: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TestDataFactory:
    """Factory for generating unique test data with deterministic seeds.

    Each instance can be initialized with a seed for reproducible data, or
    use system time for true uniqueness across parallel runs.
    """

    FIRST_NAMES = [
        "alice", "bob", "charlie", "diana", "eve", "frank", "grace", "henry",
        "iris", "jack", "karen", "leo", "mia", "noah", "olivia", "peter",
    ]

    LAST_NAMES = [
        "smith", "johnson", "williams", "brown", "jones", "garcia", "miller",
        "davis", "rodriguez", "martinez", "hernandez", "lopez", "gonzalez",
    ]

    CITIES = [
        "newyork", "london", "paris", "tokyo", "berlin", "sydney", "toronto",
        "mumbai", "dublin", "amsterdam", "seoul", "singapore",
    ]

    COUNTRIES = ["us", "uk", "ca", "au", "de", "fr", "jp", "in", "ie", "nl"]

    CATEGORIES = [
        "electronics", "books", "clothing", "home", "sports", "toys",
        "automotive", "health", "garden", "music",
    ]

    PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "bank_transfer"]

    ORDER_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]

    def __init__(self, seed: Optional[int] = None) -> None:
        if seed is None:
            seed = _now_ms()
        self.seed = seed
        self._rng = random.Random(seed)
        self._run_id = f"{seed}-{_rand_alpha(4)}"

    @property
    def run_id(self) -> str:
        return self._run_id

    def _ts(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def user(self, **overrides: Any) -> User:
        first = self._rng.choice(self.FIRST_NAMES)
        last = self._rng.choice(self.LAST_NAMES)
        username = f"{first}.{last}.{_rand_alnum(6)}".lower()
        email = f"{username}@test-{self._run_id}.example.com"
        user = User(
            username=username,
            email=email,
            password="P@ssw0rd!" + _rand_digits(2),
            first_name=first.capitalize(),
            last_name=last.capitalize(),
            age=self._rng.randint(18, 80),
            phone=f"+1{_rand_digits(10)}",
            address=f"{self._rng.randint(1, 9999)} {_rand_alpha(6)} street",
            city=self._rng.choice(self.CITIES),
            country=self._rng.choice(self.COUNTRIES),
            zip_code=_rand_digits(5),
            created_at=self._ts(),
        )
        for key, value in overrides.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user

    def product(self, **overrides: Any) -> Product:
        name = f"{self._rng.choice(self.CATEGORIES).capitalize()} {_rand_alpha(5)}"
        product = Product(
            name=name,
            sku=f"SKU-{_rand_alnum(8).upper()}",
            price=round(self._rng.uniform(1.0, 999.99), 2),
            quantity=self._rng.randint(0, 500),
            category=self._rng.choice(self.CATEGORIES),
            description=f"Test product {name} - {_rand_alpha(12)}",
            weight_kg=round(self._rng.uniform(0.1, 50.0), 2),
            dimensions=f"{self._rng.randint(1, 100)}x{self._rng.randint(1, 100)}x{self._rng.randint(1, 100)}",
            in_stock=bool(self._rng.getrandbits(1)),
            created_at=self._ts(),
        )
        for key, value in overrides.items():
            if hasattr(product, key):
                setattr(product, key, value)
        return product

    def order(self, customer_email: Optional[str] = None, **overrides: Any) -> Order:
        if customer_email is None:
            customer_email = f"customer.{_rand_alpha(6)}@test-{self._run_id}.example.com"
        items: List[Dict[str, Any]] = []
        subtotal = 0.0
        for _ in range(self._rng.randint(1, 5)):
            price = round(self._rng.uniform(5.0, 200.0), 2)
            qty = self._rng.randint(1, 10)
            items.append({
                "product_id": str(uuid.uuid4()),
                "name": f"item-{_rand_alpha(5)}",
                "price": price,
                "quantity": qty,
            })
            subtotal += price * qty
        tax = round(subtotal * 0.08, 2)
        shipping = round(self._rng.uniform(0.0, 25.0), 2)
        total = round(subtotal + tax + shipping, 2)
        order = Order(
            order_number=f"ORD-{_rand_digits(8)}",
            customer_email=customer_email,
            items=items,
            subtotal=round(subtotal, 2),
            tax=tax,
            shipping=shipping,
            total=total,
            status=self._rng.choice(self.ORDER_STATUSES),
            payment_method=self._rng.choice(self.PAYMENT_METHODS),
            shipping_address=f"{self._rng.randint(1, 9999)} {_rand_alpha(6)} ave",
            created_at=self._ts(),
        )
        for key, value in overrides.items():
            if hasattr(order, key):
                setattr(order, key, value)
        return order

    def payment(self, amount: Optional[float] = None, **overrides: Any) -> PaymentDetails:
        if amount is None:
            amount = round(self._rng.uniform(1.0, 5000.0), 2)
        payment = PaymentDetails(
            card_number=f"4{_rand_digits(15)}",
            cvv=_rand_digits(3),
            expiry_month=self._rng.randint(1, 12),
            expiry_year=self._rng.randint(2025, 2035),
            cardholder_name=f"{self._rng.choice(self.FIRST_NAMES).capitalize()} {_rng.choice(self.LAST_NAMES).capitalize()}",
            amount=amount,
            currency=self._rng.choice(["usd", "eur", "gbp", "jpy"]),
            billing_address=f"{self._rng.randint(1, 9999)} {_rand_alpha(6)} blvd",
        )
        for key, value in overrides.items():
            if hasattr(payment, key):
                setattr(payment, key, value)
        return payment

    def bulk_users(self, count: int) -> List[User]:
        return [self.user() for _ in range(count)]

    def bulk_products(self, count: int) -> List[Product]:
        return [self.product() for _ in range(count)]

    def bulk_orders(self, count: int) -> List[Order]:
        return [self.order() for _ in range(count)]

    def save_jsonl(self, records: List[Dict[str, Any]], filename: str) -> Path:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        path = DATA_DIR / filename
        with path.open("w", encoding="utf-8") as f:
            for record in records:
                f.write(json.dumps(record, default=str) + "\n")
        return path


_factory_instance: Optional[TestDataFactory] = None


def get_factory(seed: Optional[int] = None) -> TestDataFactory:
    """Return a process-local factory singleton (seeded once per worker)."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = TestDataFactory(seed=seed)
    return _factory_instance


def reset_factory() -> None:
    global _factory_instance
    _factory_instance = None
