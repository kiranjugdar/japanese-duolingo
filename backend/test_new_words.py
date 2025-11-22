import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# Login
login_url = f"{BASE_URL}/token"
login_data = {
    "username": "test@test.com",
    "password": "test123"
}
response = requests.post(login_url, data=login_data)
token = response.json()["access_token"]
print(f"✓ Logged in successfully\n")

# Test with fresh words
headers = {"Authorization": f"Bearer {token}"}
image_url = "http://127.0.0.1:8000/generate-image"

test_words = [
    {"word": "猫", "english_meaning": "cat"},
    {"word": "空", "english_meaning": "sky"},
    {"word": "unicorn", "english_meaning": "unicorn"},  # This should fallback to Pollinations
]

print("="*60)
print("Testing Pexels API with NEW words")
print("="*60)

for test_data in test_words:
    print(f"\n{'='*60}")
    print(f"Testing: {test_data['word']} ({test_data['english_meaning']})")
    print(f"{'='*60}")

    start = time.time()
    try:
        response = requests.post(image_url, json=test_data, headers=headers)
        elapsed = time.time() - start

        if response.status_code == 200:
            print(f"✓ Image generated successfully")
            print(f"⏱️  Client-side time: {elapsed:.2f}s")
            print(f"📦 Response size: {len(response.content):,} bytes")
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "="*60)
print("Now check backend logs to see:")
print("  ✓ Pexels API being used for common words (cat, sky)")
print("  🎨 Pollinations.ai fallback for rare words (unicorn)")
print("="*60)
