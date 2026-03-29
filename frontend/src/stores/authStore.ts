import { create } from 'zustand'

type AuthUser = {
  id: number
  username: string
}

type AuthState = {
  accessToken: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  setAccessToken: (token: string | null) => void
  setSession: (token: string, user: AuthUser) => void
  clear: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  user: null,
  isAuthenticated: false,
  setAccessToken: (accessToken) =>
    set(() => ({
      accessToken,
      isAuthenticated: Boolean(accessToken),
    })),
  setSession: (accessToken, user) => set({ accessToken, user, isAuthenticated: true }),
  clear: () => set({ accessToken: null, user: null, isAuthenticated: false }),
}))
