import { beforeEach, describe, expect, it, vi } from 'vitest'
import { TWO_FACTOR_STORAGE_KEY } from './authStore'

describe('useAuthStore two-factor persistence', () => {
  beforeEach(() => {
    sessionStorage.clear()
    vi.resetModules()
  })

  it('restores an active 2FA challenge after a reload', async () => {
    const { useAuthStore } = await import('./authStore')

    useAuthStore.getState().startTwoFactor({
      challengeToken: 'challenge-token-123',
      nextAction: 'verify',
    })

    expect(sessionStorage.getItem(TWO_FACTOR_STORAGE_KEY)).toBe(
      JSON.stringify({
        required: true,
        challengeToken: 'challenge-token-123',
        nextAction: 'verify',
      }),
    )

    vi.resetModules()

    const { useAuthStore: reloadedStore } = await import('./authStore')
    expect(reloadedStore.getState().twoFactor).toEqual({
      required: true,
      challengeToken: 'challenge-token-123',
      nextAction: 'verify',
    })
  })

  it('clears the persisted challenge when a session is established', async () => {
    const { useAuthStore } = await import('./authStore')

    useAuthStore.getState().startTwoFactor({
      challengeToken: 'challenge-token-123',
      nextAction: 'setup',
    })

    useAuthStore.getState().setSession('access-token-123', { id: 1, username: 'alice' })

    expect(sessionStorage.getItem(TWO_FACTOR_STORAGE_KEY)).toBeNull()
    expect(useAuthStore.getState().twoFactor).toEqual({
      required: false,
      challengeToken: null,
      nextAction: null,
    })
  })
})