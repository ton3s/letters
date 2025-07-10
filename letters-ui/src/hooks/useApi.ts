import { useState, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
}

interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T | null>;
  reset: () => void;
}

export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<T>
): UseApiReturn<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    error: null,
    isLoading: false,
  });

  const execute = useCallback(
    async (...args: any[]): Promise<T | null> => {
      setState({ data: null, error: null, isLoading: true });

      try {
        const result = await apiFunction(...args);
        setState({ data: result, error: null, isLoading: false });
        return result;
      } catch (error) {
        setState({
          data: null,
          error: error instanceof Error ? error : new Error('Unknown error'),
          isLoading: false,
        });
        return null;
      }
    },
    [apiFunction]
  );

  const reset = useCallback(() => {
    setState({ data: null, error: null, isLoading: false });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}