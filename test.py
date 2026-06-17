import hashlib

password = input("Enter password: ")

pass_hash = hashlib.sha256(
    password.encode()
).hexdigest()

print(pass_hash)