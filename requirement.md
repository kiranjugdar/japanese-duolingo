Role: Expert Full Stack Developer (Next.js App Router + Python FastAPI).

Goal: Build a stateless Japanese learning app with a split-screen interface.
Architecture:

Backend (Python FastAPI):
Create a single route POST /generate.
It accepts a list of excluded_words (strings) to avoid duplicates.
It uses OpenAI (gpt-4o-mini) to generate 3 new beginner Japanese words.
Output JSON: jp_word, reading (kana), romaji, english, image_search_term (for finding an image).
Enable CORS for localhost:3000.

Frontend (Next.js + Tailwind):
Hook (useWordQueue): Automatically fetches data from the API. When the queue has fewer than 2 items, it fetches more in the background to ensure infinite scrolling without loading screens.

UI (Split Screen):
Left: Shows Japanese word. Includes a generic Unsplash image (source: https://source.unsplash.com/random/?<image_search_term>) or a placeholder if that fails. Includes a button to trigger window.speechSynthesis for the Japanese word.
Right: Initially blurred (filter: blur(12px)). Clicking anywhere on the screen reveals the English translation and Romaji.
Navigation: A "Next" button appears only after the word is revealed.

Styling:
Use Tailwind CSS.
Design for mobile-first (vertical split) and Desktop (horizontal split).
Use large, friendly typography.

Constraints:
No database.
No user auth.
Handle API loading states gracefully (skeleton loaders).

Output:
Please provide the main.py code, requirements.txt, page.tsx, and the custom hook file.