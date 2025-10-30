import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'

import { RankTrainPage } from '@/pages/RankTrainPage'
import { ToastContainer } from '@/components/ui/toaster'
import type { JobRecord } from '@/components/JobForm'
import api from '@/lib/axios'
vi.mock('@/lib/axios', () => {
  const get = vi.fn()
  const post = vi.fn()
  return {
    default: {
      get,
      post
    }
  }
})

const mockedApi = api as unknown as {
  get: vi.Mock
  post: vi.Mock
}

describe('RankTrainPage', () => {
  beforeEach(() => {
    mockedApi.get.mockReset()
    mockedApi.post.mockReset()
    mockedApi.get.mockImplementation((url: string) => {
      if (url === '/models') {
        return Promise.resolve({
          data: {
            weights: [0.5, 0.18, 0.1, 0.17, 0.05],
            lr: 0.1,
            l2: 0.0001,
            updated_at: '2024-01-01T00:00:00Z'
          }
        })
      }
      if (url === '/rankings') {
        return Promise.resolve({
          data: {
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
          }
        })
      }
      return Promise.reject(new Error(`Unexpected get ${url}`))
    })
    mockedApi.post.mockResolvedValue({
      data: { updated_pairs: 1, new_weights: [0.51, 0.19, 0.11, 0.18, 0.05] }
    })
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
      expect(mockedApi.get).toHaveBeenCalledWith('/rankings', expect.any(Object))
    })

    await screen.findByText(/Sample Candidate/)
  })
})
