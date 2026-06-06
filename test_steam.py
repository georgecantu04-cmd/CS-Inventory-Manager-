"""
Quick test script to debug Steam API connection
"""
import requests
from config import settings

print("Testing Steam API Connection...")
print(f"Steam ID: {settings.steam_id}")
print(f"API Key: {settings.steam_api_key[:10]}...")
print()

# Test inventory endpoint
url = f"https://steamcommunity.com/inventory/{settings.steam_id}/730/2"
params = {"l": "english", "count": 5000}

print(f"Testing URL: {url}")
print()

try:
    response = requests.get(url, params=params, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print()

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            item_count = len(data.get("assets", []))
            print(f"✓ SUCCESS! Found {item_count} items in your CS2 inventory")
        else:
            print(f"✗ Steam returned success=false")
            print(f"Response: {data}")
    else:
        print(f"✗ Failed with status {response.status_code}")
        print(f"Response text: {response.text[:500]}")

except Exception as e:
    print(f"✗ Error: {str(e)}")

print("\n" + "="*60)
print("If you see 'SUCCESS' above, your setup is correct!")
print("If not, please copy the entire output and send it to me.")
