import { create } from 'zustand'

type AuthUser = {
  id: number
  username: string
}

type TwoFactorState = {
  required: boolean
  challengeToken: string | null
  nextAction: 'setup' | 'verify' | null
}

type AuthState = {
  accessToken: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  twoFactor: TwoFactorState
  setAccessToken: (token: string | null) => void
  setSession: (token: string, user: AuthUser) => void
  startTwoFactor: (payload: { challengeToken: string; nextAction: 'setup' | 'verify' }) => void
  clearTwoFactor: () => void
  clear: () => void
}

export const TWO_FACTOR_STORAGE_KEY = 'igar.auth.twoFactor'

type StoredTwoFactorState = {
  required: boolean
  challengeToken: string | null
  nextAction: 'setup' | 'verify' | null
}

function readStoredTwoFactorState(): TwoFactorState {
  if (typeof window === 'undefined') {
    return { required: false, challengeToken: null, nextAction: null }
  }

  try {
    const rawValue = window.sessionStorage.getItem(TWO_FACTOR_STORAGE_KEY)
    if (!rawValue) {
      return { required: false, challengeToken: null, nextAction: null }
    }

    const parsedValue = JSON.parse(rawValue) as StoredTwoFactorState
    if (parsedValue.required && parsedValue.challengeToken && (parsedValue.nextAction === 'setup' || parsedValue.nextAction === 'verify')) {
      return parsedValue
    }
  } catch {
    return { required: false, challengeToken: null, nextAction: null }
  }

  return { required: false, challengeToken: null, nextAction: null }
}

function writeStoredTwoFactorState(state: TwoFactorState) {
  if (typeof window === 'undefined') {
    return
  }

  try {
    if (!state.required || !state.challengeToken || !state.nextAction) {
      window.sessionStorage.removeItem(TWO_FACTOR_STORAGE_KEY)
      return
    }

    window.sessionStorage.setItem(
      TWO_FACTOR_STORAGE_KEY,
      JSON.stringify({
        required: state.required,
        challengeToken: state.challengeToken,
        nextAction: state.nextAction,
      }),
    )
  } catch {
    // Ignore storage failures and keep the in-memory flow working.
  }
}

function clearStoredTwoFactorState() {
  writeStoredTwoFactorState({ required: false, challengeToken: null, nextAction: null })
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  isAuthenticated: false,
  twoFactor: readStoredTwoFactorState(),
  setAccessToken: (accessToken) =>
    set(() => ({
      accessToken,
      isAuthenticated: Boolean(accessToken),
    })),
  setSession: (accessToken, user) =>
    set(() => {
      clearStoredTwoFactorState()

      return {
        accessToken,
        user,
        isAuthenticated: true,
        twoFactor: { required: false, challengeToken: null, nextAction: null },
      }
    }),
  startTwoFactor: ({ challengeToken, nextAction }) =>
    set(() => {
      const twoFactorState = {
        required: true,
        challengeToken,
        nextAction,
      }
      writeStoredTwoFactorState(twoFactorState)

      return {
        accessToken: null,
        isAuthenticated: false,
        twoFactor: twoFactorState,
      }
    }),
  clearTwoFactor: () =>
    set((state) => {
      clearStoredTwoFactorState()

      return {
        ...state,
        twoFactor: { required: false, challengeToken: null, nextAction: null },
      }
    }),
  clear: () =>
    set(() => {
      clearStoredTwoFactorState()

      return {
        accessToken: null,
        user: null,
        isAuthenticated: false,
        twoFactor: { required: false, challengeToken: null, nextAction: null },
      }
    }),
}))
