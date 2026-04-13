import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { LoginPage } from './LoginPage'
import { useAuthStore } from '../stores/authStore'
import * as authApi from '../api/auth'
import '../i18n'

// Mock window.matchMedia for Ant Design responsive components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

describe('LoginPage', () => {
  beforeEach(() => {
    useAuthStore.getState().clear()
    vi.restoreAllMocks()
  })

  it('redirects to documents after successful login', async () => {
    vi.spyOn(authApi, 'requestCsrfCookie').mockResolvedValue()
    vi.spyOn(authApi, 'login').mockResolvedValue({
      access: 'token-123',
      user: { id: 7, username: 'alice' },
      two_fa_required: false,
      two_fa_verified: true,
      next_action: null,
    })

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/documents" element={<div>documents-route</div>} />
        </Routes>
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Identifiant'), {
      target: { value: 'alice' },
    })
    fireEvent.change(screen.getByLabelText('Mot de passe'), {
      target: { value: 'StrongPassword123!' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Se connecter' }))

    await waitFor(() => {
      expect(screen.getByText('documents-route')).toBeInTheDocument()
    })
    expect(useAuthStore.getState().isAuthenticated).toBe(true)
  })

  it('redirects to 2fa flow when backend requires otp', async () => {
    vi.spyOn(authApi, 'requestCsrfCookie').mockResolvedValue()
    vi.spyOn(authApi, 'login').mockResolvedValue({
      access: null,
      user: { id: 7, username: 'alice' },
      two_fa_required: true,
      two_fa_verified: false,
      next_action: 'setup',
      challenge_token: 'challenge-token',
    })

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/login/2fa" element={<div>twofa-route</div>} />
        </Routes>
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Identifiant'), {
      target: { value: 'alice' },
    })
    fireEvent.change(screen.getByLabelText('Mot de passe'), {
      target: { value: 'StrongPassword123!' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Se connecter' }))

    await waitFor(() => {
      expect(screen.getByText('twofa-route')).toBeInTheDocument()
    })
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
    expect(useAuthStore.getState().twoFactor.required).toBe(true)
  })

  it('shows backend error message when login fails', async () => {
    vi.spyOn(authApi, 'requestCsrfCookie').mockResolvedValue()
    vi.spyOn(authApi, 'login').mockRejectedValue({
      response: {
        access: 'token-123',
        data: {
          detail: 'Identifiants invalides.',
        },
      },
    })

    render(
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Identifiant'), {
      target: { value: 'alice' },
    })
    fireEvent.change(screen.getByLabelText('Mot de passe'), {
      target: { value: 'wrong' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Se connecter' }))

    await waitFor(() => {
      expect(screen.getByText('Identifiants invalides.')).toBeInTheDocument()
    })
    expect(useAuthStore.getState().isAuthenticated).toBe(false)
  })
})
