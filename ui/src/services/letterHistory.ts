import { LetterResponse } from '../types';
import { msalInstance } from '../auth/authConfig';

export interface StoredLetter extends LetterResponse {
  id: string;
  savedAt: string;
  customerName: string;
  letterType: string;
}

const STORAGE_KEY_PREFIX = 'letter_history';
const MAX_HISTORY_SIZE = 50;

export class LetterHistoryService {
  // Get the current user's ID for storage key
  private static getUserStorageKey(): string {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      const userId = accounts[0].localAccountId || accounts[0].homeAccountId || 'default';
      return `${STORAGE_KEY_PREFIX}_${userId}`;
    }
    return `${STORAGE_KEY_PREFIX}_default`;
  }

  // Get all letters from localStorage for the current user
  static getAll(): StoredLetter[] {
    try {
      const storageKey = this.getUserStorageKey();
      const stored = localStorage.getItem(storageKey);
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
      
      const storageKey = this.getUserStorageKey();
      localStorage.setItem(storageKey, JSON.stringify(history));
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
        
        const storageKey = this.getUserStorageKey();
        localStorage.setItem(storageKey, JSON.stringify(history));
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
        const storageKey = this.getUserStorageKey();
        localStorage.setItem(storageKey, JSON.stringify(filtered));
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Error deleting letter:', error);
      return false;
    }
  }

  // Clear all history for the current user
  static clearAll(): void {
    const storageKey = this.getUserStorageKey();
    localStorage.removeItem(storageKey);
  }
}