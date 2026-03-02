import requests
import base64
import os

HOST = "https://dbc-f4d6132c-6cc4.cloud.databricks.com"  # your host
TOKEN = "your_token"  # your token

headers = {"Authorization": f"Bearer {TOKEN}"}

# Read CSV
with open("data/modern_cards.csv", "rb") as f:
    content = f.read()

# Upload in chunks via DBFS API
# Create file
requests.post(f"{HOST}/api/2.0/dbfs/mkdirs",
    headers=headers,
    json={"path": "/deck-confidant/raw"}
)

# Upload file
encoded = base64.b64encode(content).decode("utf-8")
requests.post(f"{HOST}/api/2.0/dbfs/put",
    headers=headers,
    json={
        "path": "/deck-confidant/raw/modern_cards.csv",
        "contents": encoded,
        "overwrite": True
    }
)
print("Upload complete")
