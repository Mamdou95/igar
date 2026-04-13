import { apiClient } from './client'

type AuthUser = {
  id: number
  username: string
}

export type LoginResponse = {
  access: string | null
  user: AuthUser
  two_fa_required: boolean
  two_fa_verified: boolean
  next_action: 'setup' | 'verify' | null
  challenge_token?: string
}

export async function requestCsrfCookie() {
  await apiClient.get('/auth/csrf/')
}

export async function login(username: string, password: string): Promise<LoginResponse> {
  const response = await apiClient.post('/auth/login/', { username, password })
  const data = response.data as {
    access: string | null
    user: AuthUser
    ['2fa_required']?: boolean
    ['2fa_verified']?: boolean
    next_action?: 'setup' | 'verify' | null
    challenge_token?: string
  }

  return {
    access: data.access ?? null,
    user: data.user,
    two_fa_required: Boolean(data['2fa_required']),
    two_fa_verified: Boolean(data['2fa_verified']),
    next_action: data.next_action ?? null,
    challenge_token: data.challenge_token,
  }
}

export async function setupTwoFactor(challengeToken: string) {
  const response = await apiClient.post('/auth/2fa/setup/', { challenge_token: challengeToken })
  return response.data as { secret: string; qr_code: string; issuer: string }
}

export async function confirmTwoFactor(challengeToken: string, otpCode: string) {
  const response = await apiClient.post('/auth/2fa/confirm/', { challenge_token: challengeToken, otp_code: otpCode })
  return response.data as { access: string; user: AuthUser }
}

export async function verifyTwoFactor(challengeToken: string, otpCode: string) {
  const response = await apiClient.post('/auth/2fa/verify/', { challenge_token: challengeToken, otp_code: otpCode })
  return response.data as { access: string; user: AuthUser }
}

export async function listTwoFactorUsers() {
  const response = await apiClient.get('/auth/2fa/users/')
  return response.data as {
    results: Array<{
      id: number
      username: string
      is_active: boolean
      is_staff: boolean
      has_2fa: boolean
      last_2fa_reset_at: string | null
      two_factor_reset_history: string[]
    }>
  }
}

export async function disableTwoFactor(userId: number) {
  const response = await apiClient.post('/auth/2fa/disable/', { user_id: userId })
  return response.data as { detail: string; user_id: number }
}
