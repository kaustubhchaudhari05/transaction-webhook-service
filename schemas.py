from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransactionWebhook(BaseModel):
    transaction_id: str = Field(min_length=1)
    source_account: str = Field(min_length=1)
    destination_account: str = Field(min_length=1)
    amount: Decimal = Field(gt=0)
    currency: str = Field(
        min_length=3,
        max_length=3,
        pattern=r"^[A-Z]{3}$",
    )


class TransactionStatusResponse(BaseModel):
    transaction_id: str
    status: str
    created_at: datetime
    processed_at: datetime | None
