import secrets

# Generate a 32-character random string
FLUTTERWAVE_SECRET_HASH = secrets.token_hex(32)
MAAS_MASTER_KEY = secrets.token_hex(32)
print(FLUTTERWAVE_SECRET_HASH)
print(MAAS_MASTER_KEY)
