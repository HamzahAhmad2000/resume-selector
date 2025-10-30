import * as React from 'react'

import { ToastProviderWithState, Toaster } from './use-toast'

export const ToastContainer: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ToastProviderWithState>
    {children}
    <Toaster />
  </ToastProviderWithState>
)
