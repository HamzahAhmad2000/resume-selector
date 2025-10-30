export interface JobRecord {
  id: number
  title: string
  description: string
}

export interface CreateJobRequest {
  title: string
  description: string
}

export interface CreateJobResponse {
  job_id: number
}

export interface UploadResumeResponse {
  candidate_id: number
  full_name: string
  email: string
  phone: string
  skills: string[]
  years_exp: number
  edu_level: number
}

export interface RankedCandidate {
  candidate_id: number
  full_name: string
  email: string
  phone: string
  skills: string[]
  years_exp: number
  edu_level_raw: number
  sem_sim: number
  skill_overlap: number
  jaccard: number
  years: number
  edu: number
  score: number
  explore: boolean
}

export interface RankingResponse {
  job_id: number
  weights: number[]
  candidates: RankedCandidate[]
}

export interface RankingParams {
  job_id: number
  k?: number
  epsilon?: number
}

export interface FeedbackRequest {
  job_id: number
  shown_candidate_ids: number[]
  chosen_candidate_id: number
}

export interface FeedbackResponse {
  updated_pairs: number
  new_weights: number[]
}

export interface ModelState {
  weights: number[]
  lr: number
  l2: number
  updated_at?: string
}
