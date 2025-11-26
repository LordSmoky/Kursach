from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

@dataclass
class Client:
    id: Optional[int]
    full_name: str
    passport_data: str
    phone_number: str
    email: str = ""
    address: str = ""
    created_at: Optional[datetime] = None

@dataclass
class Deposit:
    id: Optional[int]
    client_id: int
    deposit_type: str
    amount: Decimal
    interest_rate: Decimal
    open_date: date
    close_date: Optional[date] = None
    status: str = "active"

@dataclass
class Transaction:
    id: Optional[int]
    deposit_id: int
    type: str
    amount: Decimal
    description: str = ""
    transaction_date: Optional[datetime] = None

@dataclass
class DepositPlan:
    id: Optional[int]
    name: str
    description: str
    interest_rate: Decimal
    min_amount: Decimal
    max_amount: Optional[Decimal]
    duration_months: int
    early_withdrawal_penalty: Decimal
    is_active: bool = True
    created_at: Optional[datetime] = None