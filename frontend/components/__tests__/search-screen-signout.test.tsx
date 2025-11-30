/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock the signOut function before importing
const mockSignOut = jest.fn();
const mockUseSession = jest.fn();
const mockUseRouter = jest.fn();

jest.mock('next-auth/react', () => ({
  signOut: (...args: any[]) => mockSignOut(...args),
  useSession: () => mockUseSession(),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => mockUseRouter(),
}));

jest.mock('next/link', () => {
  return ({ children, href }: any) => <a href={href}>{children}</a>;
});

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, className, disabled, asChild, ...props }: any) => {
    if (asChild) {
      return <div className={className} {...props}>{children}</div>;
    }
    return (
      <button onClick={onClick} className={className} disabled={disabled} {...props}>
        {children}
      </button>
    );
  },
}));

jest.mock('@/components/ui/textarea', () => ({
  Textarea: ({ value, onChange, ...props }: any) => (
    <textarea value={value} onChange={onChange} {...props} />
  ),
}));

jest.mock('@/components/ui/label', () => ({
  Label: ({ children, ...props }: any) => <label {...props}>{children}</label>,
}));

jest.mock('@/components/search-command', () => ({
  SearchCommand: ({ value, onChange }: any) => (
    <input
      data-testid="search-command"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));

jest.mock('@/lib/utils', () => ({
  cn: (...classes: any[]) => classes.filter(Boolean).join(' '),
}));

// Import the component after all mocks are set up
import { SearchScreen } from '../search-screen';

describe('SearchScreen - Sign Out Button', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default router mock
    mockUseRouter.mockReturnValue({
      push: jest.fn(),
      pathname: '/',
      query: {},
      asPath: '/',
    });
  });

  it('should call signOut function when "Cerrar sesión" button is clicked', () => {
    // Arrange: Set up a session with a user
    mockUseSession.mockReturnValue({
      data: {
        user: {
          name: 'Test User',
          email: 'test@example.com',
          image: 'https://example.com/avatar.jpg',
        },
      },
      status: 'authenticated',
    });

    // Act: Render the component
    render(<SearchScreen />);

    // Open the profile dropdown
    const profileButton = screen.getByLabelText('Perfil');
    fireEvent.click(profileButton);

    // Find and click the "Cerrar sesión" button
    const signOutButton = screen.getByText('Cerrar sesión');
    fireEvent.click(signOutButton);

    // Assert: Verify that signOut was called with the correct callback URL
    expect(mockSignOut).toHaveBeenCalledWith({ callbackUrl: '/' });
    expect(mockSignOut).toHaveBeenCalledTimes(1);
  });

  it('should call signOut with correct parameters when user has no avatar', () => {
    // Arrange: Set up session without image
    mockUseSession.mockReturnValue({
      data: {
        user: {
          name: 'John Doe',
          email: 'john@example.com',
        },
      },
      status: 'authenticated',
    });

    // Act
    render(<SearchScreen />);

    // Open profile menu and click sign out
    const profileButton = screen.getByLabelText('Perfil');
    fireEvent.click(profileButton);
    
    const signOutButton = screen.getByText('Cerrar sesión');
    fireEvent.click(signOutButton);

    // Assert
    expect(mockSignOut).toHaveBeenCalledWith({ callbackUrl: '/' });
  });

  it('should not display sign out button when user is not logged in', () => {
    // Arrange: No session
    mockUseSession.mockReturnValue({
      data: null,
      status: 'unauthenticated',
    });

    // Act
    render(<SearchScreen />);

    // Assert: Profile button should not exist
    expect(screen.queryByLabelText('Perfil')).not.toBeInTheDocument();
    expect(screen.queryByText('Cerrar sesión')).not.toBeInTheDocument();
  });
});
