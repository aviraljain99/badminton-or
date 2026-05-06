import ReactECharts from 'echarts-for-react'
import type { WinRateMatrix } from '../utils/stats'

interface Props {
  data: WinRateMatrix
}

export function WinRateHeatmap({ data }: Props) {
  const { playerIds, playerNames, matrix } = data
  const names = playerIds.map((id) => playerNames[id])

  // ECharts heatmap data format: [xIndex, yIndex, value]
  // x = column (partner j), y = row (partner i), only lower diagonal (i > j)
  const seriesData: [number, number, number][] = []
  for (let i = 0; i < playerIds.length; i++) {
    for (let j = 0; j < i; j++) {
      const val = matrix[i][j]
      if (val !== null) seriesData.push([j, i, val])
    }
  }

  const option = {
    tooltip: {
      formatter: (params: { data: [number, number, number] }) => {
        const [xi, yi, val] = params.data
        return `${names[yi]} & ${names[xi]}<br/>Win rate: ${(val * 100).toFixed(1)}%`
      },
    },
    grid: { top: 20, right: 80, bottom: 90, left: 110 },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { rotate: 45, fontSize: 11 },
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { fontSize: 11 },
    },
    visualMap: {
      min: 0,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 8,
      inRange: { color: ['#d73027', '#fee08b', '#1a9850'] },
    },
    series: [
      {
        type: 'heatmap',
        data: seriesData,
        label: { show: true, formatter: (p: { data: [number, number, number] }) => p.data[2].toFixed(2) },
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 480 }} />
}