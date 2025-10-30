import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'

const LABELS = ['Semantic', 'Skill overlap', 'Jaccard', 'Experience', 'Education']

interface WeightsPanelProps {
  weights: number[]
  lr: number
  l2: number
  updatedAt?: string
}

export const WeightsPanel = ({ weights, lr, l2, updatedAt }: WeightsPanelProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Model Weights</CardTitle>
        <CardDescription>Live linear coefficients with hyper-parameters.</CardDescription>
      </CardHeader>
      <CardContent className='space-y-2'>
        <ul className='space-y-1 text-sm'>
          {LABELS.map((label, index) => (
            <li className='flex justify-between rounded-md border border-border px-3 py-1.5' key={label}>
              <span>{label}</span>
              <span className='font-mono'>{(weights[index] ?? 0).toFixed(3)}</span>
            </li>
          ))}
        </ul>
        <div className='grid grid-cols-2 gap-2 text-sm text-muted-foreground'>
          <span>Learning rate</span>
          <span className='text-right font-mono'>{lr.toFixed(3)}</span>
          <span>L2 penalty</span>
          <span className='text-right font-mono'>{l2.toExponential(1)}</span>
        </div>
        {updatedAt && <p className='text-xs text-muted-foreground'>Updated {updatedAt}</p>}
      </CardContent>
    </Card>
  )
}
