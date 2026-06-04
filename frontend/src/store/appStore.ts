import { create } from 'zustand'

interface AppStore {
  sidebarCollapsed: boolean
  activeWorkspace: string
  notificationCount: number
  theme: 'light' | 'dark'
  setSidebarCollapsed: (v: boolean) => void
  setActiveWorkspace: (w: string) => void
  toggleTheme: () => void
}

export const useAppStore = create<AppStore>((set) => ({
  sidebarCollapsed: false,
  activeWorkspace: 'Acme Corp',
  notificationCount: 7,
  theme: (localStorage.getItem('theme') as 'light' | 'dark') ?? 'dark',
  setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
  setActiveWorkspace: (w) => set({ activeWorkspace: w }),
  toggleTheme: () => set((s) => {
    const next = s.theme === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', next)
    return { theme: next }
  }),
}))
