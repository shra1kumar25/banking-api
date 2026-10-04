from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.models import users, accounts, transactions
from app.auth import (
    create_token,
    get_current_user,
    verify_password,
    hash_password,
)


router = APIRouter()


# -------------------------
# Request Models
# -------------------------

class DepositRequest(BaseModel):
    account_number: str
    amount: float


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str


# -------------------------
# Role Authorization
# -------------------------

def admin_required(user):

    if user["role"] != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin Access Required"
        )


def manager_required(user):

    if user["role"] != "BANK_MANAGER":
        raise HTTPException(
            status_code=403,
            detail="Manager Access Required"
        )


def customer_required(user):

    if user["role"] != "CUSTOMER":
        raise HTTPException(
            status_code=403,
            detail="Customer Access Required"
        )


def teller_required(user):

    if user["role"] != "TELLER":
        raise HTTPException(
            status_code=403,
            detail="Teller Access Required"
        )


def transaction_required(user):

    if user["role"] not in ["BANK_MANAGER", "TELLER"]:
        raise HTTPException(
            status_code=403,
            detail="Transaction Access Required"
        )


def auditor_required(user):

    if user["role"] != "AUDITOR":
        raise HTTPException(
            status_code=403,
            detail="Auditor Access Required"
        )


# -------------------------
# Login
# -------------------------

@router.post("/login")
def login(data: dict):

    for user in users:

        if user["username"] == data["username"]:

            if verify_password(
                data["password"],
                user["password"]
            ):

                token = create_token(user)

                return {
                    "access_token": token
                }

            break

    raise HTTPException(
        status_code=401,
        detail="Invalid Credentials"
    )


# -------------------------
# ADMIN - View Users
# -------------------------

@router.get("/users")
def view_users(
    user=Depends(get_current_user)
):

    admin_required(user)

    safe_users = []

    for item in users:

        safe_users.append({
            "id": item["id"],
            "username": item["username"],
            "role": item["role"]
        })

    return safe_users


# -------------------------
# ADMIN - Create User
# -------------------------

@router.post("/users")
def create_user(
    request: UserCreateRequest,
    user=Depends(get_current_user)
):

    admin_required(user)

    new_user = {
        "id": len(users) + 1,
        "username": request.username,
        "password": hash_password(request.password),
        "role": request.role
    }

    users.append(new_user)

    return {
        "message": "User Created Successfully",
        "user": {
            "id": new_user["id"],
            "username": new_user["username"],
            "role": new_user["role"]
        }
    }


# -------------------------
# BANK MANAGER - View Accounts
# -------------------------

@router.get("/accounts")
def view_accounts(
    user=Depends(get_current_user)
):

    manager_required(user)

    return accounts


# -------------------------
# CUSTOMER - Own Account
# -------------------------

@router.get("/my-account")
def my_account(
    user=Depends(get_current_user)
):

    customer_required(user)

    for account in accounts:

        if account["customer"] == user["username"]:

            return account

    raise HTTPException(
        status_code=404,
        detail="Account Not Found"
    )


# -------------------------
# BANK MANAGER + TELLER
# Deposit
# -------------------------

@router.post("/deposit")
def deposit(
    request: DepositRequest,
    user=Depends(get_current_user)
):

    transaction_required(user)

    for account in accounts:

        if account["account_number"] == request.account_number:

            account["balance"] += request.amount

            transactions.append({
                "account_number": account["account_number"],
                "type": "DEPOSIT",
                "amount": request.amount,
                "performed_by": user["username"]
            })

            return {
                "message": "Deposit Successful",
                "new_balance": account["balance"]
            }

    raise HTTPException(
        status_code=404,
        detail="Account Not Found"
    )


# -------------------------
# BANK MANAGER + TELLER
# Withdraw
# -------------------------

@router.post("/withdraw")
def withdraw(
    request: DepositRequest,
    user=Depends(get_current_user)
):

    transaction_required(user)

    for account in accounts:

        if account["account_number"] == request.account_number:

            if request.amount > account["balance"]:

                raise HTTPException(
                    status_code=400,
                    detail="Insufficient Funds"
                )

            account["balance"] -= request.amount

            transactions.append({
                "account_number": account["account_number"],
                "type": "WITHDRAW",
                "amount": request.amount,
                "performed_by": user["username"]
            })

            return {
                "message": "Withdrawal Successful",
                "new_balance": account["balance"]
            }

    raise HTTPException(
        status_code=404,
        detail="Account Not Found"
    )


# -------------------------
# AUDITOR - View Transactions
# -------------------------

@router.get("/transactions")
def view_transactions(
    user=Depends(get_current_user)
):

    auditor_required(user)

    return transactions
