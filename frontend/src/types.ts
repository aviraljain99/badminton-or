export interface Player {
  id: string
  name: string
}

export interface Game {
  team1_player1: string
  team1_player2: string
  team1_score: number
  team2_player1: string
  team2_player2: string
  team2_score: number
}

export interface CourtTimeEntry {
  id: string
  name: string
  courtTimeMin: number
}