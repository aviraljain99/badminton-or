import ReactECharts from 'echarts-for-react'
import type { CourtTimeEntry } from '../types'

interface Props {
  data: CourtTimeEntry[]
  selectedIds: Set<string>
}

export function CourtTimeChart({ data, selectedIds }: Props) {
  const filtered = data
    .filter((d) => selectedIds.has(d.id) && d.courtTimeMin > 0)
    .sort((a, b) => b.courtTimeMin - a.courtTimeMin)

  const option = {
    tooltip: {
      formatter: (params: { name: string; value: number }) =>
        `${params.name}: ${params.value.toFixed(0)} min`,
    },
    grid: { top: 20, right: 70, bottom: 30, left: 110 },
    xAxis: {
      type: 'value',
      name: 'Court Time (min)',
      nameLocation: 'end',
      nameGap: 8,
    },
    yAxis: {
      type: 'category',
      data: filtered.map((d) => d.name),
      axisLabel: { fontSize: 11 },
    },
    series: [
      {
        type: 'bar',
        data: filtered.map((d) => d.courtTimeMin),
        label: {
          show: true,
          position: 'right',
          formatter: (p: { value: number }) => `${p.value.toFixed(0)}m`,
        },
        itemStyle: { color: '#4a90d9' },
      },
    ],
  }

  return (
    <ReactECharts
      option={option}
      style={{ height: Math.max(200, filtered.length * 32 + 60) }}
    />
  )
}