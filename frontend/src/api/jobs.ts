import api from '@/lib/axios'
import type { CreateJobRequest, CreateJobResponse } from '@/types/api'

export async function createJob(payload: CreateJobRequest): Promise<CreateJobResponse> {
  const response = await api.post<CreateJobResponse>('/jobs', payload)
  return response.data
}
