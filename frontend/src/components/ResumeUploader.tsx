import { ChangeEvent, DragEvent, useCallback, useMemo, useState } from 'react'

import api from '@/lib/axios'
import { cn } from '@/lib/utils'
import { Badge } from './ui/badge'
import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { useToast } from './ui/use-toast'

type UploadStatus = 'pending' | 'uploading' | 'success' | 'error'

interface UploadItem {
  file: File
  status: UploadStatus
  message?: string
  candidateId?: number
}

interface ResumeUploaderProps {
  disabled?: boolean
}

export const ResumeUploader = ({ disabled }: ResumeUploaderProps) => {
  const [items, setItems] = useState<UploadItem[]>([])
  const [isDragging, setDragging] = useState(false)
  const { toastSuccess, toastError } = useToast()

  const queueUpload = useCallback((files: FileList | null) => {
    if (!files || files.length === 0) return
    const newItems: UploadItem[] = []
    Array.from(files).forEach((file) => {
      if (file.type !== 'application/pdf') {
        toastError({ title: 'Only PDFs accepted', description: `${file.name} skipped.` })
        return
      }
      if (file.size > 10 * 1024 * 1024) {
        toastError({ title: 'File too large', description: `${file.name} exceeds 10MB limit.` })
        return
      }
      newItems.push({ file, status: 'pending' })
    })
    if (newItems.length === 0) return
    setItems((prev) => [...prev, ...newItems])
  }, [toastError])

  const handleDrop = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragging(false)
    if (disabled) return
    queueUpload(event.dataTransfer.files)
  }, [queueUpload, disabled])

  const handleDragOver = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    if (disabled) return
    setDragging(true)
  }, [disabled])

  const handleDragLeave = useCallback((event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragging(false)
  }, [])

  const uploadAll = useCallback(async () => {
    for (const item of items) {
      if (item.status === 'success') continue
      setItems((prev) => prev.map((entry) => (entry.file === item.file ? { ...entry, status: 'uploading' } : entry)))
      const formData = new FormData()
      formData.append('file', item.file)
      try {
        const response = await api.post('/resumes', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
        const candidateId = response.data.candidate_id as number
        setItems((prev) =>
          prev.map((entry) => (entry.file === item.file ? { ...entry, status: 'success', candidateId } : entry))
        )
        toastSuccess({ title: 'Resume ingested', description: `${item.file.name} → candidate ${candidateId}` })
      } catch (error) {
        setItems((prev) =>
          prev.map((entry) => (entry.file === item.file ? { ...entry, status: 'error', message: 'Upload failed' } : entry))
        )
        toastError({ title: 'Upload failed', description: `${item.file.name} could not be saved.` })
      }
    }
  }, [items, toastError, toastSuccess])

  const handleFileInput = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    queueUpload(event.target.files)
  }, [queueUpload])

  const pendingCount = useMemo(() => items.filter((item) => item.status !== 'success').length, [items])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Upload Resumes</CardTitle>
        <CardDescription>Drag in one or more resume PDFs. Maximum size 10MB per file.</CardDescription>
      </CardHeader>
      <CardContent className='space-y-4'>
        <div
          className={cn(
            'flex h-40 w-full flex-col items-center justify-center rounded-lg border-2 border-dashed border-muted-foreground/40 bg-muted/30 text-center transition-colors',
            isDragging && 'border-primary bg-primary/5'
          )}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          role='presentation'
        >
          <p className='text-sm text-muted-foreground'>Drop PDF resumes here or select manually.</p>
          <input
            aria-label='Upload resume'
            className='mt-4 cursor-pointer'
            disabled={disabled}
            multiple
            onChange={handleFileInput}
            type='file'
            accept='application/pdf'
          />
        </div>
        <div className='flex items-center justify-between'>
          <p className='text-sm text-muted-foreground'>Queued files: {items.length}</p>
          <Button disabled={disabled || items.length === 0} onClick={uploadAll} variant='secondary'>
            {pendingCount === 0 ? 'Re-upload' : 'Upload all'}
          </Button>
        </div>
        <ul className='space-y-2'>
          {items.map((item) => (
            <li key={item.file.name} className='flex items-center justify-between rounded-md border border-border px-3 py-2'>
              <div>
                <p className='text-sm font-medium'>{item.file.name}</p>
                <p className='text-xs text-muted-foreground'>{(item.file.size / 1024).toFixed(1)} KB</p>
              </div>
              <Badge variant={item.status === 'success' ? 'success' : item.status === 'error' ? 'destructive' : 'secondary'}>
                {item.status === 'uploading' && 'Uploading…'}
                {item.status === 'pending' && 'Pending'}
                {item.status === 'success' && `Stored #${item.candidateId}`}
                {item.status === 'error' && (item.message ?? 'Error')}
              </Badge>
            </li>
          ))}
          {items.length === 0 && <li className='text-sm text-muted-foreground'>No resumes queued yet.</li>}
        </ul>
      </CardContent>
    </Card>
  )
}
