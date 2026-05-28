import type { Game, Player } from '../types'

export interface WinRateMatrix {
  playerIds: string[]
  playerNames: Record<string, string>
  // matrix[i][j] = win rate when playerIds[i] and playerIds[j] play as a pair (null if no games)
  // only the lower diagonal (i > j) is populated, mirroring the notebook
  matrix: (number | null)[][]
}

export interface PartnershipEdge {
  source: string
  target: string
  games: number
  wins: number
}

export function computeWinRates(
  games: Game[],
  players: Player[],
  selectedIds: Set<string>,
): WinRateMatrix {
  const selected = players.filter((p) => selectedIds.has(p.id))
  const playerIds = selected.map((p) => p.id)
  const playerNames: Record<string, string> = {}
  selected.forEach((p) => (playerNames[p.id] = p.name))

  const idx: Record<string, number> = {}
  playerIds.forEach((id, i) => (idx[id] = i))
  const n = playerIds.length

  const wins = Array.from({ length: n }, () => new Array<number>(n).fill(0))
  const total = Array.from({ length: n }, () => new Array<number>(n).fill(0))

  for (const g of games) {
    const allFour = [g.team1_player1, g.team1_player2, g.team2_player1, g.team2_player2]
    if (!allFour.every((p) => selectedIds.has(p))) continue

    const t1Won = g.team1_score > g.team2_score
    const pairs: [[string, string], boolean][] = [
      [[g.team1_player1, g.team1_player2], t1Won],
      [[g.team2_player1, g.team2_player2], !t1Won],
    ]
    for (const [[p1, p2], won] of pairs) {
      const i = idx[p1]
      const j = idx[p2]
      total[i][j]++
      total[j][i]++
      if (won) {
        wins[i][j]++
        wins[j][i]++
      }
    }
  }

  const matrix: (number | null)[][] = Array.from({ length: n }, (_, i) =>
    Array.from({ length: n }, (_, j) => {
      if (i <= j) return null
      return total[i][j] > 0 ? wins[i][j] / total[i][j] : null
    }),
  )

  return { playerIds, playerNames, matrix }
}

export function computePartnerships(
  games: Game[],
  players: Player[],
  selectedIds: Set<string>,
): {
  nodes: { id: string; name: string; gameCount: number }[]
  edges: PartnershipEdge[]
} {
  const nameMap: Record<string, string> = {}
  players.forEach((p) => (nameMap[p.id] = p.name))

  const edgeMap = new Map<string, PartnershipEdge>()

  for (const g of games) {
    const allFour = [g.team1_player1, g.team1_player2, g.team2_player1, g.team2_player2]
    if (!allFour.every((p) => selectedIds.has(p))) continue

    const t1Won = g.team1_score > g.team2_score
    const pairs: [[string, string], boolean][] = [
      [[g.team1_player1, g.team1_player2], t1Won],
      [[g.team2_player1, g.team2_player2], !t1Won],
    ]
    for (const [[p1, p2], won] of pairs) {
      const key = [p1, p2].sort().join('|')
      if (!edgeMap.has(key)) {
        edgeMap.set(key, { source: p1, target: p2, games: 0, wins: 0 })
      }
      const e = edgeMap.get(key)!
      e.games++
      if (won) e.wins++
    }
  }

  const edges = Array.from(edgeMap.values())

  const gameCount: Record<string, number> = {}
  edges.forEach((e) => {
    gameCount[e.source] = (gameCount[e.source] ?? 0) + e.games
    gameCount[e.target] = (gameCount[e.target] ?? 0) + e.games
  })

  const nodeIds = new Set(edges.flatMap((e) => [e.source, e.target]))
  const nodes = Array.from(nodeIds).map((id) => ({
    id,
    name: nameMap[id] ?? id,
    gameCount: gameCount[id] ?? 0,
  }))

  return { nodes, edges }
}