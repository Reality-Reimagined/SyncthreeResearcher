import streamlit_authenticator as stauth

# Replace 'abc123' and 'def456' with the actual passwords you want to use
hashed_passwords = stauth.Hasher(['raz']).generate()

print(hashed_passwords)
