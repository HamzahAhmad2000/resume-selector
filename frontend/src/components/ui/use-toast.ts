import * as React from 'react'

import { Toast, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport } from './toast'

type ToastVariant = 'default' | 'destructive' | 'success'

interface ToastRecord {
  id: string
  title?: React.ReactNode
  description?: React.ReactNode
  action?: React.ReactNode
  variant?: ToastVariant
}

const ToastContext = React.createContext<{
  toasts: ToastRecord[]
  setToasts: React.Dispatch<React.SetStateAction<ToastRecord[]>>
} | null>(null)

export const ToastProviderWithState: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = React.useState<ToastRecord[]>([])
  return <ToastContext.Provider value={{ toasts, setToasts }}>{children}</ToastContext.Provider>
}

let count = 0

export function useToast() {
  const ctx = React.useContext(ToastContext)
  if (!ctx) {
    throw new Error('useToast must be used inside ToastProviderWithState')
  }

  const dismiss = React.useCallback((id: string) => {
    ctx.setToasts((state) => state.filter((item) => item.id !== id))
  }, [ctx])

  const toast = React.useCallback(
    (options: Omit<ToastRecord, 'id'>) => {
      const id = `toast-${count++}`
      ctx.setToasts((state) => [...state, { ...options, id }])
      return {
        id,
        dismiss: () => dismiss(id)
      }
    },
    [ctx, dismiss]
  )

  const createToastByVariant = React.useCallback(
    (variant: ToastVariant) =>
      (options: Omit<ToastRecord, 'id' | 'variant'>) =>
        toast({ ...options, variant }),
    [toast]
  )

  return {
    toasts: ctx.toasts,
    toast,
    dismiss,
    toastSuccess: createToastByVariant('success'),
    toastError: createToastByVariant('destructive')
  }
}

export const Toaster: React.FC = () => {
  const ctx = React.useContext(ToastContext)
  if (!ctx) {
    throw new Error('Toaster must be used inside ToastProviderWithState')
  }
  return (
    <ToastProvider>
      {ctx.toasts.map((toastItem) => (
        <Toast key={toastItem.id} variant={toastItem.variant} onOpenChange={(open) => !open && ctx.setToasts((prev) => prev.filter((t) => t.id !== toastItem.id))} open>
          {toastItem.title && <ToastTitle>{toastItem.title}</ToastTitle>}
          {toastItem.description && <ToastDescription>{toastItem.description}</ToastDescription>}
          <ToastClose />
          {toastItem.action}
        </Toast>
      ))}
      <ToastViewport />
    </ToastProvider>
  )
}
