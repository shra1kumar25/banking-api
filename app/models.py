from app.auth import hash_password


users = [
    {
        "id": 1,
        "username": "admin",
        "password": hash_password("admin123"),
        "role": "ADMIN"
    },
    {
        "id": 2,
        "username": "manager",
        "password": hash_password("manager123"),
        "role": "BANK_MANAGER"
    },
    {
        "id": 3,
        "username": "teller",
        "password": hash_password("teller123"),
        "role": "TELLER"
    },
    {
        "id": 4,
        "username": "john",
        "password": hash_password("john123"),
        "role": "CUSTOMER"
    },
    {
        "id": 5,
        "username": "auditor",
        "password": hash_password("audit123"),
        "role": "AUDITOR"
    }
]


accounts = [
    {
        "account_number": "10001",
        "customer": "john",
        "balance": 50000
    }
]


transactions = []
