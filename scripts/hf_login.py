from huggingface_hub import login
from getpass import getpass

token = getpass("Paste your Hugging Face WRITE token here: ")
login(token=token)

print("Hugging Face login successful.")