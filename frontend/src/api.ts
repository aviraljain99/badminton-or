import type { CourtTimeEntry, Game, Player } from './types'

const BASE = 'http://localhost:8000'

export async function fetchPlayers(): Promise<Player[]> {
  const res = await fetch(`${BASE}/api/players`)
  return res.json()
}

export async function fetchGames(): Promise<Game[]> {
  const res = await fetch(`${BASE}/api/games`)
  return res.json()
}

export async function fetchCourtTime(): Promise<CourtTimeEntry[]> {
  const res = await fetch(`${BASE}/api/court-time`)
  return res.json()
}