import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# Try to signup first (in case user doesn't exist)
signup_url = f"{BASE_URL}/signup"
signup_data = {
    "email": "test@test.com",
    "password": "test123"
}

print("Signing up (or skipping if already exists)...")
try:
    response = requests.post(signup_url, json=signup_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Signup successful, got token")
    else:
        # User already exists, try to login
        print("User exists, logging in...")
        login_url = f"{BASE_URL}/token"
        login_data = {
            "username": "test@test.com",
            "password": "test123"
        }
        response = requests.post(login_url, data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✓ Login successful, got token")
        else:
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            exit(1)
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# Now test image generation
headers = {"Authorization": f"Bearer {token}"}
image_url = "http://127.0.0.1:8000/generate-image"

test_words = [
    {"word": "りんご", "english_meaning": "apple"},
    {"word": "ねこ", "english_meaning": "cat"},
    {"word": "りんご", "english_meaning": "apple"},  # Test cache
]

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
            print(f"📦 Response size: {len(response.content)} bytes")
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "="*60)
print("Check the backend server logs above for detailed timing!")
print("="*60)
