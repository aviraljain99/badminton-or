import { useEffect, useState } from 'react'
import { fetchCourtTime, fetchGames, fetchPlayers } from './api'
import { CourtTimeChart } from './components/CourtTimeChart'
import { PartnershipGraph } from './components/PartnershipGraph'
import { PlayerToggle } from './components/PlayerToggle'
import { WinRateHeatmap } from './components/WinRateHeatmap'
import type { CourtTimeEntry, Game, Player } from './types'
import { computePartnerships, computeWinRates } from './utils/stats'

export default function App() {
  const [players, setPlayers] = useState<Player[]>([])
  const [games, setGames] = useState<Game[]>([])
  const [courtTime, setCourtTime] = useState<CourtTimeEntry[]>([])
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([fetchPlayers(), fetchGames(), fetchCourtTime()])
      .then(([p, g, ct]) => {
        setPlayers(p)
        setGames(g)
        setCourtTime(ct)
        setSelected(new Set(p.map((pl) => pl.id)))
        setLoading(false)
      })
      .catch(() => {
        setError('Could not connect to the backend. Is uvicorn running on port 8000?')
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="status-screen">Loading...</div>
  if (error) return <div className="status-screen error">{error}</div>

  const winRateData = computeWinRates(games, players, selected)
  const { nodes, edges } = computePartnerships(games, players, selected)

  return (
    <div className="app">
      <header className="header">
        <h1>Badminton Dashboard</h1>
      </header>
      <div className="layout">
        <aside className="sidebar">
          <PlayerToggle players={players} selected={selected} onChange={setSelected} />
        </aside>
        <main className="main">
          <section className="chart-section">
            <h2>Team Pair Win Rate</h2>
            {winRateData.playerIds.length >= 2 ? (
              <WinRateHeatmap data={winRateData} />
            ) : (
              <p className="empty">Select at least 2 players.</p>
            )}
          </section>

          <section className="chart-section">
            <h2>Partnership Graph</h2>
            {nodes.length >= 2 ? (
              <PartnershipGraph nodes={nodes} edges={edges} />
            ) : (
              <p className="empty">Select at least 2 players.</p>
            )}
          </section>

          <section className="chart-section">
            <h2>Court Time per Player</h2>
            <CourtTimeChart data={courtTime} selectedIds={selected} />
          </section>
        </main>
      </div>
    </div>
  )
}