import { useCallback, useEffect, useMemo, useState } from 'react'

import { Rankings, RankedCandidate } from '@/components/Rankings'
import { WeightsPanel } from '@/components/WeightsPanel'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import api from '@/lib/axios'
import { useToast } from '@/components/ui/use-toast'
import type { JobRecord } from '@/components/JobForm'

const DEFAULT_WEIGHTS = [0.5, 0.18, 0.1, 0.17, 0.05]

interface RankTrainPageProps {
  jobs: JobRecord[]
  currentJobId: number | null
  onSelectJob: (jobId: number) => void
}

interface ModelMeta {
  lr: number
  l2: number
  updatedAt?: string
}

export const RankTrainPage = ({ jobs, currentJobId, onSelectJob }: RankTrainPageProps) => {
  const [selectedJobId, setSelectedJobId] = useState<number | null>(currentJobId)
  const [epsilon, setEpsilon] = useState(0.1)
  const [k, setK] = useState(5)
  const [weights, setWeights] = useState<number[]>(DEFAULT_WEIGHTS)
  const [candidates, setCandidates] = useState<RankedCandidate[]>([])
  const [modelMeta, setModelMeta] = useState<ModelMeta>({ lr: 0.1, l2: 1e-4 })
  const [loading, setLoading] = useState(false)
  const [shownIds, setShownIds] = useState<number[]>([])
  const { toastError, toastSuccess } = useToast()

  useEffect(() => {
    setSelectedJobId(currentJobId)
  }, [currentJobId])

  useEffect(() => {
    if (!selectedJobId && jobs.length === 1) {
      setSelectedJobId(jobs[0].id)
    }
  }, [jobs, selectedJobId])

  const pullModel = useCallback(async () => {
    try {
      const response = await api.get('/models')
      setWeights(response.data.weights ?? DEFAULT_WEIGHTS)
      setModelMeta({ lr: response.data.lr, l2: response.data.l2, updatedAt: response.data.updated_at })
    } catch (error) {
      // Silent failure keeps UI usable when backend not ready
    }
  }, [])

  useEffect(() => {
    pullModel()
  }, [pullModel])

  const fetchRankings = useCallback(async () => {
    if (!selectedJobId) {
      toastError({ title: 'Select a job', description: 'Choose a job before fetching rankings.' })
      return
    }
    setLoading(true)
    try {
      const response = await api.get('/rankings', {
        params: {
          job_id: selectedJobId,
          k,
          epsilon
        }
      })
      const data = response.data
      setWeights(data.weights ?? DEFAULT_WEIGHTS)
      setCandidates(data.candidates as RankedCandidate[])
      setShownIds((data.candidates as RankedCandidate[]).map((candidate) => candidate.candidate_id))
    } catch (error) {
      toastError({ title: 'Rankings failed', description: 'Ensure the backend is running and resumes are ingested.' })
    } finally {
      setLoading(false)
    }
  }, [selectedJobId, epsilon, k, toastError])

  const handlePick = useCallback(async (candidateId: number) => {
    if (!selectedJobId) {
      toastError({ title: 'No job selected', description: 'Pick a job before sending feedback.' })
      return
    }
    if (shownIds.length === 0) {
      toastError({ title: 'No rankings yet', description: 'Fetch rankings before training the model.' })
      return
    }

    try {
      await api.post('/feedback', {
        job_id: selectedJobId,
        shown_candidate_ids: shownIds,
        chosen_candidate_id: candidateId
      })
      toastSuccess({ title: 'Model updated', description: 'Feedback incorporated. Regenerating rankings…' })
      await fetchRankings()
      await pullModel()
    } catch (error) {
      toastError({ title: 'Feedback failed', description: 'Could not update weights. Please retry.' })
    }
  }, [fetchRankings, pullModel, selectedJobId, shownIds, toastError, toastSuccess])

  const jobLabel = useMemo(() => {
    if (!selectedJobId) return 'No job selected'
    const job = jobs.find((item) => item.id === selectedJobId)
    return job ? job.title : `Job #${selectedJobId}`
  }, [jobs, selectedJobId])

  return (
    <div className='grid gap-6 lg:grid-cols-[2fr_1fr]'>
      <div className='space-y-6'>
        <Card>
          <CardHeader>
            <CardTitle>Controls</CardTitle>
            <CardDescription>Pick a job, set exploration, and request Top-K rankings.</CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='grid gap-4 md:grid-cols-2'>
              <div className='space-y-2'>
                <Label htmlFor='job-select'>Job</Label>
                <select
                  className='h-10 w-full rounded-md border border-input bg-background px-3 text-sm'
                  id='job-select'
                  onChange={(event) => {
                    const raw = event.target.value
                    if (raw === '') {
                      setSelectedJobId(null)
                      return
                    }
                    const value = Number(raw)
                    if (Number.isNaN(value)) {
                      setSelectedJobId(null)
                      return
                    }
                    setSelectedJobId(value)
                    onSelectJob(value)
                  }}
                  value={selectedJobId ?? ''}
                >
                  <option value=''>
                    Select a job
                  </option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title}
                    </option>
                  ))}
                </select>
              </div>
              <div className='space-y-2'>
                <Label htmlFor='k-value'>Top-K</Label>
                <input
                  className='h-10 w-full rounded-md border border-input bg-background px-3 text-sm'
                  id='k-value'
                  min={1}
                  onChange={(event) => setK(Number(event.target.value))}
                  type='number'
                  value={k}
                />
              </div>
            </div>
            <div className='space-y-2'>
              <Label htmlFor='epsilon'>Exploration ε ({epsilon.toFixed(2)})</Label>
              <input
                className='w-full'
                id='epsilon'
                max={0.3}
                min={0}
                onChange={(event) => setEpsilon(Number(event.target.value))}
                step={0.01}
                type='range'
                value={epsilon}
              />
            </div>
            <div className='flex items-center justify-between'>
              <div className='text-sm text-muted-foreground'>
                Current job: <span className='font-medium text-foreground'>{jobLabel}</span>
              </div>
              <Button disabled={!selectedJobId || loading} onClick={fetchRankings} variant='secondary'>
                {loading ? 'Fetching…' : 'Fetch Rankings'}
              </Button>
            </div>
          </CardContent>
        </Card>
        <Rankings candidates={candidates} loading={loading} onPick={handlePick} weights={weights} />
      </div>
      <div className='space-y-6'>
        <WeightsPanel l2={modelMeta.l2} lr={modelMeta.lr} updatedAt={modelMeta.updatedAt} weights={weights} />
      </div>
    </div>
  )
}
