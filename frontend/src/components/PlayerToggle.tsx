import type { Player } from '../types'

interface Props {
  players: Player[]
  selected: Set<string>
  onChange: (selected: Set<string>) => void
}

export function PlayerToggle({ players, selected, onChange }: Props) {
  const allSelected = selected.size === players.length

  const toggleAll = () => {
    onChange(allSelected ? new Set() : new Set(players.map((p) => p.id)))
  }

  const toggle = (id: string) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    onChange(next)
  }

  return (
    <div className="player-toggle">
      <div className="toggle-header">
        <span>Players</span>
        <button onClick={toggleAll}>{allSelected ? 'Deselect All' : 'Select All'}</button>
      </div>
      <div className="toggle-list">
        {players.map((p) => (
          <label key={p.id} className={`toggle-item ${selected.has(p.id) ? 'active' : ''}`}>
            <input type="checkbox" checked={selected.has(p.id)} onChange={() => toggle(p.id)} />
            {p.name}
          </label>
        ))}
      </div>
    </div>
  )
}