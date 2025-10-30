import api from '@/lib/axios'
import type { ModelState } from '@/types/api'

export async function fetchModelState(): Promise<ModelState> {
  const response = await api.get<ModelState>('/models')
  return response.data
}
