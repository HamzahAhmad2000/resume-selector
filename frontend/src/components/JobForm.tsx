import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'

import api from '@/lib/axios'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Textarea } from './ui/textarea'
import { useToast } from './ui/use-toast'

const jobSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().min(30, 'Description should be at least 30 characters')
})

type JobFormValues = z.infer<typeof jobSchema>

export interface JobRecord {
  id: number
  title: string
  description: string
}

interface JobFormProps {
  onCreated: (job: JobRecord) => void
}

export const JobForm = ({ onCreated }: JobFormProps) => {
  const { register, handleSubmit, reset, formState } = useForm<JobFormValues>({
    resolver: zodResolver(jobSchema),
    defaultValues: { title: '', description: '' }
  })
  const { toastSuccess, toastError } = useToast()
  const [isSubmitting, setSubmitting] = useState(false)

  const onSubmit = async (values: JobFormValues) => {
    setSubmitting(true)
    try {
      const response = await api.post('/jobs', values)
      const id = response.data.job_id as number
      onCreated({ id, title: values.title, description: values.description })
      toastSuccess({ title: 'Job created', description: `Stored job “${values.title}” with id ${id}` })
      reset()
    } catch (error) {
      toastError({ title: 'Could not create job', description: 'Check backend availability and try again.' })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Create Job</CardTitle>
        <CardDescription>Provide the role title and description to anchor rankings.</CardDescription>
      </CardHeader>
      <CardContent>
        <form className='space-y-4' onSubmit={handleSubmit(onSubmit)}>
          <div className='space-y-2'>
            <Label htmlFor='title'>Title</Label>
            <Input id='title' placeholder='Machine Learning Engineer' {...register('title')} />
            {formState.errors.title && <p className='text-sm text-red-600'>{formState.errors.title.message}</p>}
          </div>
          <div className='space-y-2'>
            <Label htmlFor='description'>Description</Label>
            <Textarea
              id='description'
              placeholder='Summarise responsibilities, required skills, and preferred experience.'
              rows={8}
              {...register('description')}
            />
            {formState.errors.description && <p className='text-sm text-red-600'>{formState.errors.description.message}</p>}
          </div>
          <Button disabled={isSubmitting} type='submit'>
            {isSubmitting ? 'Saving…' : 'Create Job'}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
