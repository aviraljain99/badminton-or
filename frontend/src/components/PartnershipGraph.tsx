import ReactECharts from 'echarts-for-react'
import type { PartnershipEdge } from '../utils/stats'

interface Props {
  nodes: { id: string; name: string; gameCount: number }[]
  edges: PartnershipEdge[]
}

export function PartnershipGraph({ nodes, edges }: Props) {
  const maxGames = Math.max(...edges.map((e) => e.games), 1)

  const option = {
    tooltip: {
      formatter: (params: { dataType: string; data: { name?: string; source?: string; target?: string; games?: number; wins?: number } }) => {
        if (params.dataType === 'edge') {
          const { source, target, games, wins } = params.data
          const wr = games && games > 0 ? (((wins ?? 0) / games) * 100).toFixed(1) : '0'
          return `${source} & ${target}<br/>Games: ${games}<br/>Win rate: ${wr}%`
        }
        return params.data.name ?? ''
      },
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: nodes.map((n) => ({
          id: n.id,
          name: n.name,
          symbolSize: 20 + n.gameCount * 1.5,
          label: { show: true, fontSize: 11 },
          itemStyle: { color: '#4a90d9' },
        })),
        links: edges.map((e) => ({
          source: e.source,
          target: e.target,
          games: e.games,
          wins: e.wins,
          lineStyle: {
            width: 1 + (e.games / maxGames) * 8,
            // green for high win rate, red for low
            color: `hsl(${Math.round((e.wins / e.games) * 120)}, 65%, 42%)`,
          },
        })),
        force: { repulsion: 200, edgeLength: [80, 200] },
        roam: true,
        emphasis: { focus: 'adjacency' },
      },
    ],
  }

  return <ReactECharts option={option} style={{ height: 500 }} />
}