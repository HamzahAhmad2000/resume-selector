import api from '@/lib/axios'
import type { FeedbackRequest, FeedbackResponse } from '@/types/api'

export async function sendFeedback(payload: FeedbackRequest): Promise<FeedbackResponse> {
  const response = await api.post<FeedbackResponse>('/feedback', payload)
  return response.data
}
