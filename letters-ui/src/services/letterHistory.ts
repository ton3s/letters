import { LetterResponse } from '../types';

const STORAGE_KEY = 'letter_history';

export interface StoredLetter extends LetterResponse {
  id: string;
  savedAt: string;
  customerName: string;
  letterType: string;
}

export class LetterHistoryService {
  // Get all letters from localStorage
  static getAll(): StoredLetter[] {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch (error) {
      console.error('Error reading letter history:', error);
      return [];
    }
  }

  // Save a new letter
  static save(letter: LetterResponse, customerName: string, letterType: string): void {
    try {
      const history = this.getAll();
      const storedLetter: StoredLetter = {
        ...letter,
        id: letter.document_id || `letter_${Date.now()}`,
        savedAt: new Date().toISOString(),
        customerName,
        letterType,
      };
      
      // Add to beginning of array (most recent first)
      history.unshift(storedLetter);
      
      // Keep only last 50 letters
      if (history.length > 50) {
        history.splice(50);
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Error saving letter to history:', error);
    }
  }

  // Get a specific letter by ID
  static getById(id: string): StoredLetter | undefined {
    const history = this.getAll();
    return history.find(letter => letter.id === id);
  }

  // Delete a letter by ID
  static delete(id: string): boolean {
    try {
      const history = this.getAll();
      const filtered = history.filter(letter => letter.id !== id);
      
      if (filtered.length === history.length) {
        return false; // Letter not found
      }
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
      return true;
    } catch (error) {
      console.error('Error deleting letter:', error);
      return false;
    }
  }

  // Clear all history
  static clearAll(): void {
    localStorage.removeItem(STORAGE_KEY);
  }
}