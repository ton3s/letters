import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginButton } from '../auth/LoginButton';

// Mock the auth hook
const mockLogin = jest.fn();
jest.mock('../../auth/AuthProvider', () => ({
  useAuth: () => ({
    login: mockLogin,
    isLoading: false
  })
}));

describe('LoginButton Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders with default props', () => {
    render(<LoginButton />);
    const button = screen.getByText(/Sign In/i);
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('bg-red-600');
  });

  test('renders with secondary variant', () => {
    render(<LoginButton variant="secondary" />);
    const button = screen.getByText(/Sign In/i);
    expect(button).toHaveClass('bg-white');
  });

  test('renders without icon when showIcon is false', () => {
    render(<LoginButton showIcon={false} />);
    const button = screen.getByText(/Sign In/i);
    expect(button.querySelector('svg')).not.toBeInTheDocument();
  });

  test('calls login when clicked', async () => {
    render(<LoginButton />);
    const button = screen.getByText(/Sign In/i);
    
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledTimes(1);
    });
  });

  test('shows loading state', () => {
    jest.mock('../../auth/AuthProvider', () => ({
      useAuth: () => ({
        login: mockLogin,
        isLoading: true
      })
    }));

    render(<LoginButton />);
    const button = screen.getByText(/Signing in.../i);
    expect(button).toBeDisabled();
    expect(button).toHaveClass('opacity-50');
  });

  test('applies custom className', () => {
    render(<LoginButton className="custom-class" />);
    const button = screen.getByText(/Sign In/i);
    expect(button).toHaveClass('custom-class');
  });
});