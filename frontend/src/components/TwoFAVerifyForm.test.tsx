import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { TwoFAVerifyForm } from './TwoFAVerifyForm'
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

describe('TwoFAVerifyForm', () => {
  it('validates a 6-digit OTP and submits the form', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)

    render(
      <TwoFAVerifyForm loading={false} errorMessage={null} submitLabel="Verifier" onSubmit={onSubmit} />,
    )

    fireEvent.change(screen.getByLabelText('Code a 6 chiffres'), { target: { value: '1234' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verifier' }))

    await waitFor(() => {
      expect(screen.getByText('Le code OTP doit contenir 6 chiffres.')).toBeInTheDocument()
    })
    expect(onSubmit).not.toHaveBeenCalled()

    fireEvent.change(screen.getByLabelText('Code a 6 chiffres'), { target: { value: '123456' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verifier' }))

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith('123456')
    })
  })
})
