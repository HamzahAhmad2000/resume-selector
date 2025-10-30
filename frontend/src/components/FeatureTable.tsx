import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'
import type { RankedCandidate } from './Rankings'

export interface FeatureTableFeature {
  key: keyof Pick<RankedCandidate, 'sem_sim' | 'skill_overlap' | 'jaccard' | 'years' | 'edu'>
  label: string
}

interface FeatureTableProps {
  candidate: RankedCandidate
  weights: number[]
  features: FeatureTableFeature[]
}

export const FeatureTable = ({ candidate, weights, features }: FeatureTableProps) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Feature</TableHead>
          <TableHead>Weight</TableHead>
          <TableHead>Value</TableHead>
          <TableHead>Contribution</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {features.map((feature, index) => {
          const weight = weights[index] ?? 0
          const value = candidate[feature.key] as number
          const contribution = weight * value
          return (
            <TableRow key={feature.key}>
              <TableCell>{feature.label}</TableCell>
              <TableCell className='font-mono'>{weight.toFixed(3)}</TableCell>
              <TableCell className='font-mono'>{value.toFixed(3)}</TableCell>
              <TableCell className='font-mono'>{contribution.toFixed(3)}</TableCell>
            </TableRow>
          )
        })}
      </TableBody>
    </Table>
  )
}
