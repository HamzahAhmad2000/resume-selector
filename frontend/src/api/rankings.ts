import api from '@/lib/axios'
import type { RankingParams, RankingResponse } from '@/types/api'

export async function fetchRankings(params: RankingParams): Promise<RankingResponse> {
  const response = await api.get<RankingResponse>('/rankings', { params })
  return response.data
}
