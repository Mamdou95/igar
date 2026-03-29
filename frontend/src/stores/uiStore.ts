import { create } from 'zustand'

type UiState = {
  sidebarCollapsed: boolean
  language: 'fr' | 'en'
  setSidebarCollapsed: (collapsed: boolean) => void
  toggleSidebar: () => void
  setLanguage: (language: 'fr' | 'en') => void
}

export const useUiStore = create<UiState>((set) => ({
  sidebarCollapsed: false,
  language: 'fr',
  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setLanguage: (language) => set({ language }),
}))
