import { useEffect } from 'react'

interface UseKeyboardShortcutsOptions {
  onPaste: (value: string) => void | Promise<void>
  onCancel: () => void
  isLoading: boolean
  canCancel: boolean
}

function isEditableElement(target: EventTarget | null): boolean {
  if (!(target instanceof HTMLElement)) return false
  if (target instanceof HTMLInputElement) return true
  if (target instanceof HTMLTextAreaElement) return true
  return target.isContentEditable
}

export function useKeyboardShortcuts({
  onPaste,
  onCancel,
  isLoading,
  canCancel,
}: UseKeyboardShortcutsOptions): void {
  useEffect(() => {
    const handleKeyDown = async (event: KeyboardEvent) => {
      const key = event.key.toLowerCase()

      if ((event.ctrlKey || event.metaKey) && key === 'v') {
        if (isLoading || isEditableElement(event.target)) return

        event.preventDefault()

        try {
          const text = await navigator.clipboard.readText()
          const trimmed = text.trim()
          if (!trimmed) return
          await onPaste(trimmed)
        } catch (error) {
          console.error('Clipboard access denied:', error)
        }

        return
      }

      if (event.key === 'Escape' && canCancel) {
        event.preventDefault()
        onCancel()
      }
    }

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [canCancel, isLoading, onCancel, onPaste])
}
