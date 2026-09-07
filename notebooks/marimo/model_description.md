# Badminton Scheduler — Model Description

A session has a fixed number of rounds and courts. Each round, every court hosts one doubles match: two teams of two players each. Players who are not assigned to any court in a given round are on a break.

The scheduler decides who plays with whom, on which court, and in which round, subject to the constraints below. It optimises several objectives simultaneously.

---

## Hard Constraints

### 1. One court per player per round
A player can appear on at most one court in any given round. They cannot be in two places at once.

### 2. Exactly one pair per team slot per game
Every game on every court in every round must have exactly one pair assigned to team 0 and exactly one pair assigned to team 1. A game cannot be understaffed or double-booked.

### 3. Player avoidance
Certain players have expressed a preference never to be partnered with specific other players. The scheduler hard-enforces these: an avoided pair is never assigned to the same team on the same court in the same round.

### 4. No two consecutive breaks
A player cannot sit out two rounds in a row. If they are on break in round `r`, they must play in round `r+1`. This prevents any player from going cold for an extended stretch. This only applies across rounds the player is actually available for (see constraint 6) — a round the player is away for is an absence, not a break.

### 5. Members play at least as many games as casuals
Players marked as members are prioritised. Every member is guaranteed to play at least as many total games across the session as every casual player.

### 6. Player allocations
`PLAYER_ALLOCATIONS` in the session config records round-level availability rules per player, using 1-indexed round numbers:

- `must_play` — the player is forced to be scheduled in these rounds
- `must_not_play` — the player is forced to sit out these rounds
- `unavailable_from` — the player is absent from this round onward (e.g. leaves early)
- `available_from` — the player is absent before this round (e.g. arrives late)

Rounds a player is unavailable for are treated as absences: the player is not scheduled, and the "no two consecutive breaks" rule is not enforced across them.

---

## Soft Objectives

The model maximises a weighted sum of the following objectives. All objectives are expressed in the same scaled unit so their weights are directly comparable.

### 1. Partner preferences
Some players have expressed ranked preferences for who they would like to be partnered with. The model rewards assigning preferred partners together, with higher-ranked preferences receiving a larger reward. Players with no stated preferences are treated neutrally. When both players in a pair have a preference for each other, the two scores are averaged rather than added, so a mutually-preferred pair is counted once, not twice.

### 2. Partnership variety
The model rewards each unique partnership that occurs at least once during the session. This acts as a proxy for opponent variety too: if you are paired with many different people, you naturally face many different opponents as well.

### 3. Game distribution equality
The model penalises the gap between the player who plays the most games and the player who plays the fewest. Minimising this gap means everyone gets a similar amount of court time.

### 4. Avoiding three consecutive games
Playing three rounds in a row without a break is tiring. The model penalises each occurrence of a player appearing in three consecutive rounds, nudging the scheduler to spread breaks more evenly. Players who flag `ok_with_consecutive_games` in their preferences are exempt from this penalty, so the scheduler is free to give them longer streaks.

### 5. Skill balance
Each game is scored by the absolute difference in total skill level between the two teams. The model minimises the sum of these differences across all games in the session, pushing every match toward being as evenly matched as possible.

---

## Symmetry Breaking

Two structural symmetries are broken to reduce the search space:

- **Team label symmetry**: the labels "team 0" and "team 1" within a game are arbitrary. The model canonicalises assignments so that team 0 always holds the lexicographically earlier pair, eliminating redundant mirror solutions.
- **Court ordering symmetry**: the numbering of courts within a round is arbitrary. The model enforces a fixed ordering of courts by their team-0 pair, eliminating solutions that are identical up to a permutation of court labels.

---

## Warm Start

Before solving, a greedy heuristic constructs an initial feasible allocation and feeds it to the solver as a hint. The heuristic assigns breaks by rotating fairly (players with the fewest breaks so far sit out first), then distributes the remaining players across courts by skill level using a snake-draft: the strongest and weakest active players form one team, and the two middle players form the other. This gives the solver a reasonable starting point and reduces the time spent finding the first feasible solution.
