import { useMemo, useState } from 'react'

import { type JobRecord } from './components/JobForm'
import { RankTrainPage } from './pages/RankTrainPage'
import { JobsPage } from './pages/JobsPage'
import { ResumesPage } from './pages/ResumesPage'
import { Button } from './components/ui/button'
import { ToastContainer } from './components/ui/toaster'

const TABS = [
  { id: 'jobs', label: 'Jobs' },
  { id: 'resumes', label: 'Resumes' },
  { id: 'rank', label: 'Rank & Train' }
]

type TabId = (typeof TABS)[number]['id']

const App = () => {
  const [activeTab, setActiveTab] = useState<TabId>('jobs')
  const [jobs, setJobs] = useState<JobRecord[]>([])
  const [currentJobId, setCurrentJobId] = useState<number | null>(null)

  const handleJobCreated = (job: JobRecord) => {
    setJobs((items) => [...items, job])
    setCurrentJobId(job.id)
    setActiveTab('resumes')
  }

  const handleSelectJob = (jobId: number) => {
    setCurrentJobId(jobId)
  }

  const jobActive = useMemo(() => currentJobId !== null, [currentJobId])

  return (
    <ToastContainer>
      <div className='min-h-screen bg-muted/20 pb-12'>
        <header className='border-b bg-background'>
          <div className='container flex flex-wrap items-center justify-between gap-4 py-6'>
            <div>
              <h1 className='text-2xl font-semibold'>Resume Selector</h1>
              <p className='text-sm text-muted-foreground'>Rank resumes, collect feedback, and adapt weights instantly.</p>
            </div>
            <nav className='flex gap-2'>
              {TABS.map((tab) => (
                <Button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  variant={activeTab === tab.id ? 'default' : 'ghost'}
                >
                  {tab.label}
                </Button>
              ))}
            </nav>
          </div>
        </header>
        <main className='container mt-8 space-y-6'>
          {activeTab === 'jobs' && <JobsPage jobs={jobs} onJobCreated={handleJobCreated} />}
          {activeTab === 'resumes' && <ResumesPage jobActive={jobActive} />}
          {activeTab === 'rank' && (
            <RankTrainPage currentJobId={currentJobId} jobs={jobs} onSelectJob={handleSelectJob} />
          )}
        </main>
      </div>
    </ToastContainer>
  )
}

export default App
