import api from '@/lib/axios'
import type { UploadResumeResponse } from '@/types/api'

export async function uploadResume(file: File): Promise<UploadResumeResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post<UploadResumeResponse>('/resumes', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  return response.data
}
