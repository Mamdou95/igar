import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { LoginPage } from './LoginPage'
import { useAuthStore } from '../stores/authStore'
import { apiClient } from '../api/client'
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
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { detail: 'CSRF cookie set' } })
    vi.spyOn(apiClient, 'post').mockResolvedValue({
      data: {
        access: 'token-123',
        user: { id: 7, username: 'alice' },
      },
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

  it('shows backend error message when login fails', async () => {
    vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { detail: 'CSRF cookie set' } })
    vi.spyOn(apiClient, 'post').mockRejectedValue({
      response: {
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
