from pydantic import BaseModel, Field
from typing import Literal
import time


class Intrests(BaseModel):
    date: object
    fd_number: str
    intrest: float
    user: object
    timestamp: float = Field(default_factory=time.time)


class UserInmodel(BaseModel):
    user_name: str
    password: str
    statement_name: str


class UserModel(UserInmodel):
    timestamp: float = Field(default_factory=time.time)


class Deposits(BaseModel):
    fd_number: str
    created_date: object
    amount: float
    initial_intrest_rate: float = 0
    current_intrest_rate: float = 0
    duration: int = 0
    cancelled_date: object = ""
    user: object
    status: Literal["ACTIVE", "CANCELLED"] = "ACTIVE"
    timestamp: float = Field(default_factory=time.time)


class StatementDateRange(BaseModel):
    start_date: object
    end_date: object
    user: object
    timestamp: float = Field(default_factory=time.time)