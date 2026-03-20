'use client'

import { Component, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4 px-4 text-center">
          <h2 className="text-lg font-semibold text-foreground">Terjadi Kesalahan</h2>
          <p className="text-sm text-muted-foreground max-w-md">
            Sesuatu yang tidak terduga terjadi. Coba muat ulang halaman.
          </p>
          <button
            type="button"
            onClick={() => {
              this.setState({ hasError: false })
              window.location.reload()
            }}
            className="rounded-lg bg-amber-500 px-4 py-2 text-sm font-medium text-zinc-950 transition-colors hover:bg-amber-400"
          >
            Muat Ulang
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
