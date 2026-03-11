import base64
print("=== GOOGLE_CREDENTIALS_JSON ===")
with open('credentials.json', 'r') as f:
    print(f.read())
print("\n=== TOKEN_PICKLE_B64 ===")
with open('token.pickle', 'rb') as f:
    print(base64.b64encode(f.read()).decode('utf-8'))
