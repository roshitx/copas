import { create } from 'zustand'
import type { DownloadStatus, MediaResult, Platform } from '@/types'

interface DownloadState {
  url: string
  platform: Platform
  status: DownloadStatus
  result: MediaResult | null
  error: string | null
  errorCode: string | null
  downloadProgress: number
  downloadStatus: 'idle' | 'downloading' | 'complete' | 'error'
  downloadETA: string | null

  setUrl: (url: string) => void
  setPlatform: (platform: Platform) => void
  setStatus: (status: DownloadStatus) => void
  setResult: (result: MediaResult) => void
  setError: (error: string, code?: string) => void
  setErrorCode: (code: string | null) => void
  setDownloadProgress: (progress: number) => void
  setDownloadStatus: (status: 'idle' | 'downloading' | 'complete' | 'error') => void
  setDownloadETA: (eta: string | null) => void
  reset: () => void
  resetDownloadProgress: () => void
}

const initialState = {
  url: '',
  platform: 'unknown' as Platform,
  status: 'idle' as DownloadStatus,
  result: null,
  error: null,
  errorCode: null,
  downloadProgress: 0,
  downloadStatus: 'idle' as const,
  downloadETA: null,
}

export const useDownloadStore = create<DownloadState>((set) => ({
  ...initialState,

  setUrl: (url) => set({ url }),
  setPlatform: (platform) => set({ platform }),
  setStatus: (status) => set({ status }),
  setResult: (result) => set({ result, status: 'success', error: null }),
  setError: (error, code) => set({ error, errorCode: code ?? null, status: 'error', result: null }),
  setErrorCode: (code) => set({ errorCode: code }),
  setDownloadProgress: (progress) => set({ downloadProgress: progress }),
  setDownloadStatus: (status) => set({ downloadStatus: status }),
  setDownloadETA: (eta) => set({ downloadETA: eta }),
  reset: () => set(initialState),
  resetDownloadProgress: () => set({
    downloadProgress: 0,
    downloadStatus: 'idle',
    downloadETA: null,
  }),
}))
