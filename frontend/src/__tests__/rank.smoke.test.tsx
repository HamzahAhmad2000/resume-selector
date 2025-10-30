import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'

import { RankTrainPage } from '@/pages/RankTrainPage'
import { ToastContainer } from '@/components/ui/toaster'
import type { JobRecord } from '@/types/api'
import { fetchModelState } from '@/api/models'
import { fetchRankings } from '@/api/rankings'
import { sendFeedback } from '@/api/feedback'

vi.mock('@/api/models', () => ({
  fetchModelState: vi.fn()
}))

vi.mock('@/api/rankings', () => ({
  fetchRankings: vi.fn()
}))

vi.mock('@/api/feedback', () => ({
  sendFeedback: vi.fn()
}))

const mockedFetchModelState = fetchModelState as unknown as vi.Mock
const mockedFetchRankings = fetchRankings as unknown as vi.Mock
const mockedSendFeedback = sendFeedback as unknown as vi.Mock

describe('RankTrainPage', () => {
  beforeEach(() => {
    mockedFetchModelState.mockReset()
    mockedFetchRankings.mockReset()
    mockedSendFeedback.mockReset()

    mockedFetchModelState.mockResolvedValue({
      weights: [0.5, 0.18, 0.1, 0.17, 0.05],
      lr: 0.1,
      l2: 0.0001,
      updated_at: '2024-01-01T00:00:00Z'
    })
    mockedFetchRankings.mockResolvedValue({
      job_id: 1,
      weights: [0.5, 0.18, 0.1, 0.17, 0.05],
      candidates: [
        {
          candidate_id: 1,
          full_name: 'Sample Candidate',
          email: 'sample@example.com',
          phone: '555-111-2222',
          skills: ['python', 'docker'],
          years_exp: 5,
          edu_level_raw: 3,
          sem_sim: 0.8,
          skill_overlap: 0.7,
          jaccard: 0.6,
          years: 0.4,
          edu: 0.75,
          score: 0.65,
          explore: false
        }
      ]
    })
    mockedSendFeedback.mockResolvedValue({ updated_pairs: 1, new_weights: [0.51, 0.19, 0.11, 0.18, 0.05] })
  })

  it('renders and fetches rankings', async () => {
    const jobs: JobRecord[] = [
      {
        id: 1,
        title: 'ML Engineer',
        description: 'Focus on Python and PyTorch.'
      }
    ]

    render(
      <ToastContainer>
        <RankTrainPage currentJobId={1} jobs={jobs} onSelectJob={() => {}} />
      </ToastContainer>
    )

    const fetchButton = await screen.findByRole('button', { name: /fetch rankings/i })
    fireEvent.click(fetchButton)

    await waitFor(() => {
      expect(mockedFetchRankings).toHaveBeenCalledWith({ job_id: 1, k: 5, epsilon: 0.1 })
    })

    await screen.findByText(/Sample Candidate/)
  })
})
