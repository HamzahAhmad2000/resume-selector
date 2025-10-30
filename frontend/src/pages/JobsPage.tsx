import { JobForm } from '@/components/JobForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { JobRecord } from '@/types/api'

interface JobsPageProps {
  onJobCreated: (job: JobRecord) => void
  jobs: JobRecord[]
}

export const JobsPage = ({ onJobCreated, jobs }: JobsPageProps) => {
  return (
    <div className='grid gap-6 lg:grid-cols-[2fr_1fr]'>
      <JobForm onCreated={onJobCreated} />
      <Card>
        <CardHeader>
          <CardTitle>Recent Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className='space-y-3 text-sm'>
            {jobs.map((job) => (
              <li className='rounded-md border border-border p-3' key={job.id}>
                <p className='font-medium'>{job.title}</p>
                <p className='text-xs text-muted-foreground truncate'>{job.description}</p>
              </li>
            ))}
            {jobs.length === 0 && <li className='text-muted-foreground'>No jobs created yet.</li>}
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
