import { ResumeUploader } from '@/components/ResumeUploader'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

interface ResumesPageProps {
  jobActive: boolean
}

export const ResumesPage = ({ jobActive }: ResumesPageProps) => {
  return (
    <div className='space-y-6'>
      <ResumeUploader disabled={!jobActive} />
      {!jobActive && (
        <Card>
          <CardHeader>
            <CardTitle>Heads up</CardTitle>
            <CardDescription>Create a job first to ensure resumes are scored against the right description.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className='text-sm text-muted-foreground'>Use the Job form tab to define the JD before uploading resumes.</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
