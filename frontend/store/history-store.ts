import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Platform } from '@/types'

interface HistoryEntry {
  url: string
  platform: Platform
  title: string
  thumbnail: string | null
  timestamp: number
}

interface HistoryState {
  entries: HistoryEntry[]
  addEntry: (entry: Omit<HistoryEntry, 'timestamp'>) => void
  clearAll: () => void
}

const MAX_ENTRIES = 20

export const useHistoryStore = create<HistoryState>()(
  persist(
    (set) => ({
      entries: [],
      addEntry: (entry) =>
        set((state) => {
          const exists = state.entries.some((e) => e.url === entry.url)
          const updated = exists
            ? state.entries.map((e) =>
                e.url === entry.url ? { ...e, ...entry, timestamp: Date.now() } : e
              )
            : [{ ...entry, timestamp: Date.now() }, ...state.entries]
          return { entries: updated.slice(0, MAX_ENTRIES) }
        }),
      clearAll: () => set({ entries: [] }),
    }),
    { name: 'copas-history' }
  )
)
