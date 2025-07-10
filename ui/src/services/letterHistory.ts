import { LetterResponse } from '../types';

export interface StoredLetter extends LetterResponse {
  id: string;
  savedAt: string;
  customerName: string;
  letterType: string;
}

const STORAGE_KEY = 'letter_history';
const MAX_HISTORY_SIZE = 50;

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
      
      // Add to beginning of array
      history.unshift(storedLetter);
      
      // Limit history size
      if (history.length > MAX_HISTORY_SIZE) {
        history.splice(MAX_HISTORY_SIZE);
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

  // Update an existing letter
  static update(id: string, updates: Partial<StoredLetter>): boolean {
    try {
      const history = this.getAll();
      const index = history.findIndex(letter => letter.id === id);
      
      if (index !== -1) {
        history[index] = {
          ...history[index],
          ...updates,
          savedAt: new Date().toISOString(),
        };
        
        localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error updating letter:', error);
      return false;
    }
  }

  // Delete a letter by ID
  static delete(id: string): boolean {
    try {
      const history = this.getAll();
      const filtered = history.filter(letter => letter.id !== id);
      
      if (filtered.length !== history.length) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
        return true;
      }
      
      return false;
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