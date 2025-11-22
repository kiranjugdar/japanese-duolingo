import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from './useAuth';

export interface Word {
    jp_word: string;
    reading: string;
    romaji: string;
    english: string;
    image_search_term: string;
}

export const useWordQueue = () => {
    const { token } = useAuth();
    const [queue, setQueue] = useState<Word[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const fetchedWordsRef = useRef<Set<string>>(new Set());
    const isFetchingRef = useRef(false);

    const fetchWords = useCallback(async () => {
        if (isFetchingRef.current) return;
        isFetchingRef.current = true;
        setIsLoading(true);
        setError(null);

        try {
            if (!token) return; // Don't fetch if no token

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({}), // No longer need excluded_words, handled by backend
            });

            if (!response.ok) {
                throw new Error('Failed to fetch words');
            }

            const data = await response.json();
            const newWords = data.words;

            // Add to set to avoid duplicates in future requests
            newWords.forEach((w: Word) => fetchedWordsRef.current.add(w.jp_word));

            setQueue((prev) => [...prev, ...newWords]);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
            isFetchingRef.current = false;
        }
    }, [token]);

    // Initial fetch
    useEffect(() => {
        if (queue.length === 0 && !isFetchingRef.current) {
            fetchWords();
        }
    }, [fetchWords, queue.length]);

    // Background fetch when queue is low
    useEffect(() => {
        if (queue.length < 2 && queue.length > 0 && !isFetchingRef.current) {
            fetchWords();
        }
    }, [queue.length, fetchWords]);

    const popWord = useCallback(() => {
        setQueue((prev) => {
            const newQueue = [...prev];
            newQueue.shift();
            return newQueue;
        });
    }, []);

    // Note: Images are now generated on-demand with caching
    // No need to prefetch since local generation is fast and images are cached

    return {
        currentWord: queue[0] || null,
        isLoading: isLoading && queue.length === 0, // Only show loading if queue is empty
        error,
        popWord,
    };
};

