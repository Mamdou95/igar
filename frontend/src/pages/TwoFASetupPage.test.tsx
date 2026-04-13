import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { TwoFASetupPage } from './TwoFASetupPage'
import { useAuthStore } from '../stores/authStore'
import * as authApi from '../api/auth'
import '../i18n'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

describe('TwoFASetupPage', () => {
  beforeEach(() => {
    useAuthStore.getState().clear()
    useAuthStore.getState().startTwoFactor({ challengeToken: 'challenge-123', nextAction: 'setup' })
    vi.restoreAllMocks()
  })

  it('renders QR code and submits confirmation', async () => {
    vi.spyOn(authApi, 'setupTwoFactor').mockResolvedValue({
      secret: 'SECRET',
      qr_code: 'data:image/png;base64,abc',
      issuer: 'Igar',
    })
    vi.spyOn(authApi, 'confirmTwoFactor').mockResolvedValue({
      access: 'token-123',
      user: { id: 7, username: 'alice' },
    })

    render(
      <MemoryRouter initialEntries={['/login/2fa/setup']}>
        <Routes>
          <Route path="/login/2fa/setup" element={<TwoFASetupPage />} />
          <Route path="/documents" element={<div>documents-route</div>} />
        </Routes>
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByAltText('QR code de configuration 2FA')).toBeInTheDocument()
    })

    fireEvent.change(screen.getByLabelText('Code a 6 chiffres'), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: 'Confirmer le 2FA' }))

    await waitFor(() => {
      expect(screen.getByText('documents-route')).toBeInTheDocument()
    })
    expect(useAuthStore.getState().isAuthenticated).toBe(true)
  })
})
