import { useMemo } from 'react'

import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'
import { FeatureTable, FeatureTableFeature } from './FeatureTable'

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

interface RankingsProps {
  candidates: RankedCandidate[]
  weights: number[]
  onPick: (candidateId: number) => void
  loading?: boolean
}

const EDUCATION_LABELS: Record<number, string> = {
  0: 'No degree',
  1: 'Diploma',
  2: 'Bachelor',
  3: 'Master',
  4: 'PhD'
}

const FEATURE_METADATA: FeatureTableFeature[] = [
  { key: 'sem_sim', label: 'Semantic match' },
  { key: 'skill_overlap', label: 'Skill overlap' },
  { key: 'jaccard', label: 'Jaccard score' },
  { key: 'years', label: 'Experience (norm)' },
  { key: 'edu', label: 'Education (norm)' }
]

const maskEmail = (email: string) => {
  if (!email) return '—'
  const [name, domain] = email.split('@')
  if (!domain) return '—'
  const maskedName = name.length <= 2 ? name[0] + '***' : `${name[0]}***${name[name.length - 1]}`
  return `${maskedName}@${domain}`
}

const maskPhone = (phone: string) => {
  if (!phone) return '—'
  const digits = phone.replace(/\D/g, '')
  if (digits.length <= 4) return phone
  const masked = phone.replace(/\d(?=(?:\D*\d){4})/g, '•')
  return masked
}

export const Rankings = ({ candidates, weights, onPick, loading }: RankingsProps) => {
  const averageScore = useMemo(() => {
    if (candidates.length === 0) return 0
    return candidates.reduce((acc, item) => acc + item.score, 0) / candidates.length
  }, [candidates])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rankings</CardTitle>
        <CardDescription>
          {candidates.length === 0 && 'No candidates ranked yet. Upload resumes and fetch rankings.'}
          {candidates.length > 0 && `Showing ${candidates.length} candidates. Average score ${(averageScore).toFixed(3)}.`}
        </CardDescription>
      </CardHeader>
      <CardContent className='space-y-6'>
        <div className='overflow-x-auto rounded-lg border'>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Phone</TableHead>
                <TableHead>Years</TableHead>
                <TableHead>Education</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Details</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {candidates.map((candidate) => (
                <TableRow key={candidate.candidate_id}>
                  <TableCell className='font-medium'>{candidate.full_name}</TableCell>
                  <TableCell>{maskEmail(candidate.email)}</TableCell>
                  <TableCell>{maskPhone(candidate.phone)}</TableCell>
                  <TableCell>{candidate.years_exp.toFixed(1)}</TableCell>
                  <TableCell>
                    <Badge variant='secondary'>{EDUCATION_LABELS[candidate.edu_level_raw] ?? '—'}</Badge>
                    {candidate.explore && <Badge className='ml-2' variant='outline'>Explore</Badge>}
                  </TableCell>
                  <TableCell>{candidate.score.toFixed(3)}</TableCell>
                  <TableCell>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size='sm' variant='ghost'>Insights</Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>{candidate.full_name}</DialogTitle>
                          <DialogDescription>
                            Contact: {candidate.email || '—'} · {candidate.phone || '—'}
                          </DialogDescription>
                        </DialogHeader>
                        <div className='space-y-3'>
                          <div>
                            <h4 className='text-sm font-semibold'>Skills</h4>
                            <p className='text-sm text-muted-foreground'>{candidate.skills.join(', ') || 'No skills parsed.'}</p>
                          </div>
                          <FeatureTable candidate={candidate} features={FEATURE_METADATA} weights={weights} />
                        </div>
                      </DialogContent>
                    </Dialog>
                  </TableCell>
                  <TableCell>
                    <Button disabled={loading} onClick={() => onPick(candidate.candidate_id)}>Pick as Best</Button>
                  </TableCell>
                </TableRow>
              ))}
              {candidates.length === 0 && (
                <TableRow>
                  <TableCell className='text-center text-sm text-muted-foreground' colSpan={8}>
                    Fetch rankings to see scored candidates.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}
