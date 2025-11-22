"use client";

import { useState, useEffect } from "react";
import { useWordQueue } from "@/hooks/useWordQueue";

import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";

export default function Home() {
  const { currentWord, isLoading, error, popWord } = useWordQueue();
  const { isAuthenticated, token } = useAuth();
  const router = useRouter();
  const [isRevealed, setIsRevealed] = useState(false);
  const [imageSrc, setImageSrc] = useState("");
  const [imageLoading, setImageLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated && !token) {
      router.push("/login");
    }
  }, [isAuthenticated, token, router]);

  useEffect(() => {
    if (currentWord && token) {
      setIsRevealed(false);
      setImageLoading(true);

      // Cleanup previous image blob URL
      if (imageSrc && imageSrc.startsWith('blob:')) {
        URL.revokeObjectURL(imageSrc);
      }
      setImageSrc("");

      // Use local SDXL generator for much faster image generation
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          word: currentWord.jp_word,
          english_meaning: currentWord.image_search_term
        }),
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob();
      })
      .then(blob => {
        const url = URL.createObjectURL(blob);
        setImageSrc(url);
        setImageLoading(false);
        console.log('Image loaded successfully for:', currentWord.jp_word);
      })
      .catch(err => {
        console.error('Error loading image:', err);
        setImageLoading(false);
        // Show error message to user
        setImageSrc("");
      });
    }
  }, [currentWord, token]);

  const handleSpeak = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (currentWord) {
      const utterance = new SpeechSynthesisUtterance(currentWord.jp_word);
      utterance.lang = "ja-JP";
      window.speechSynthesis.speak(utterance);
    }
  };

  const handleNext = (e: React.MouseEvent) => {
    e.stopPropagation();
    popWord();
  };

  const handleReveal = () => {
    if (!isRevealed) {
      setIsRevealed(true);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="animate-pulse text-2xl font-bold text-gray-400">Loading...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-red-50">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  if (!currentWord) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-gray-500">No words available.</div>
      </div>
    );
  }

  return (
    <main className="flex flex-col md:flex-row h-screen w-full overflow-hidden font-sans">
      {/* Left Side: Japanese */}
      <div className="flex-1 flex flex-col items-center justify-center bg-white p-8 relative border-b md:border-b-0 md:border-r border-gray-200">

        <div className="z-10 flex flex-col items-center gap-8 max-w-md w-full">
          {/* Image Display */}
          <div className="w-full aspect-video rounded-xl overflow-hidden shadow-lg mb-4 bg-gray-100">
            {imageLoading && (
              <div className="w-full h-full flex items-center justify-center flex-col gap-2">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
                <p className="text-sm text-gray-500">Generating image...</p>
              </div>
            )}
            {imageSrc && !imageLoading && (
              <img
                src={imageSrc}
                alt={currentWord.english}
                className="w-full h-full object-cover"
                onError={(e) => {
                  console.error('Image failed to render');
                  e.currentTarget.style.display = 'none';
                }}
              />
            )}
            {!imageSrc && !imageLoading && (
              <div className="w-full h-full flex items-center justify-center">
                <p className="text-sm text-gray-400">No image available</p>
              </div>
            )}
          </div>

          <div className="text-8xl md:text-9xl font-bold text-gray-800 text-center">
            {currentWord.jp_word}
          </div>

          <button
            onClick={handleSpeak}
            className="p-4 rounded-full bg-blue-500 hover:bg-blue-600 text-white transition-colors shadow-lg"
            aria-label="Speak"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
          </button>
        </div>
      </div>

      {/* Right Side: English / Reveal */}
      <div
        className="flex-1 flex flex-col items-center justify-center bg-gray-50 p-8 cursor-pointer relative transition-colors hover:bg-gray-100"
        onClick={handleReveal}
      >
        <div className={`transition-all duration-500 flex flex-col items-center gap-4 ${isRevealed ? 'filter-none' : 'blur-xl select-none'}`}>
          <div className="text-2xl text-gray-500 font-medium">{currentWord.reading}</div>
          <div className="text-xl text-gray-400">{currentWord.romaji}</div>
          <div className="text-6xl font-bold text-gray-800 text-center mt-4">{currentWord.english}</div>
        </div>

        {!isRevealed && (
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="text-gray-400 font-medium text-lg uppercase tracking-widest">Click to Reveal</div>
          </div>
        )}

        {isRevealed && (
          <button
            onClick={handleNext}
            className="mt-12 px-8 py-3 bg-green-500 hover:bg-green-600 text-white text-xl font-bold rounded-full shadow-lg transform transition hover:scale-105"
          >
            Next Word
          </button>
        )}
      </div>
    </main>
  );
}
