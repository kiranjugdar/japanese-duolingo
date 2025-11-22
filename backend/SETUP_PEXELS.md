# Pexels API Setup

## Why Pexels?

The app now uses **Pexels API** for fast, high-quality stock photos before falling back to AI image generation. This provides:

- **Very fast response times** (usually < 1 second)
- **High-quality stock photos** from a library of 1M+ images
- **Completely free** with generous limits:
  - 200 requests/hour
  - 20,000 requests/month
  - Unlimited requests available if you meet their terms

## How to Get Your API Key

1. Visit [https://www.pexels.com/api/](https://www.pexels.com/api/)
2. Click "Get Started" or "Sign Up"
3. Create a free account
4. Once logged in, go to your API dashboard
5. Copy your API key

## Setup

1. Open your `.env` file in the backend folder
2. Add your Pexels API key:
   ```
   PEXELS_API_KEY=your_actual_api_key_here
   ```
3. Save the file
4. Restart your backend server

## How It Works

The image endpoint now follows this strategy:

1. **Cache Check**: First checks if we already have the image in the database
2. **Pexels API**: If not cached, tries to fetch from Pexels stock photos (FAST!)
3. **AI Generation**: If Pexels doesn't have the image, falls back to Pollinations.ai

This means:
- Common words (dog, tree, apple) will load almost instantly from Pexels
- Unusual words will still get AI-generated images
- All images are cached locally after first fetch

## Testing

Run the test script to see the speed improvement:

```bash
python test_image_timing.py
```

You should see much faster response times for common English words!
