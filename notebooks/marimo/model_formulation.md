# Badminton Scheduler — Mathematical Formulation

## Sets

| Symbol | Definition |
|--------|------------|
| $P$ | Set of players |
| $\mathcal{P}$ | Set of ordered player pairs $\{(p_1, p_2) \mid p_1, p_2 \in P,\ p_1 < p_2\}$ |
| $R$ | Set of rounds $\{0, \ldots, R_{\max}-1\}$ |
| $C$ | Set of courts $\{0, \ldots, C_{\max}-1\}$ |
| $T$ | Team labels $\{0, 1\}$ |
| $P_M \subseteq P$ | Member players |
| $P_K \subseteq P$ | Casual players |
| $P_{\bar{c}} \subseteq P$ | Players exempt from the consecutive-games penalty (flagged `ok_with_consecutive_games`) |
| $A \subseteq \mathcal{P}$ | Avoided pairs (never permitted to partner) |

## Parameters

| Symbol | Definition |
|--------|------------|
| $\ell_p$ | Skill level of player $p$ |
| $s_{p_1 p_2} = \ell_{p_1} + \ell_{p_2}$ | Combined skill of pair $(p_1, p_2)$ |
| $\text{pref}(p, p')$ | Preference score player $p$ assigns to being partnered with $p'$ |
| $\text{avail}_p \subseteq R$ | Rounds player $p$ is available for (from `PLAYER_ALLOCATIONS`) |
| $\text{req}_p \subseteq \text{avail}_p$ | Rounds player $p$ is required to play |

## Decision Variables

| Variable | Type | Definition |
|----------|------|------------|
| $x_{p_1 p_2 r c t}$ | Binary | 1 if pair $(p_1, p_2)$ is assigned as team $t$ on court $c$ in round $r$ |
| $z_{p r}$ | Binary | 1 if player $p$ plays in round $r$ |
| $w_{p_1 p_2}$ | Binary | 1 if pair $(p_1, p_2)$ partners at least once during the session |
| $\text{consec3}_{p r}$ | Binary | 1 if player $p$ plays in all three of rounds $r$, $r+1$, $r+2$; defined only for $p \in P \setminus P_{\bar{c}}$ |
| $\text{diff}_{r c}$ | Integer $\geq 0$ | Absolute skill difference between the two teams in game $(r, c)$ |
| $M$ | Integer | Maximum number of games played by any player |
| $m$ | Integer | Minimum number of games played by any player |

## Hard Constraints

**C1 — One court per player per round**

$$\sum_{(p_1,p_2) \in \mathcal{P}} \sum_{c \in C} \sum_{t \in T} x_{p_1 p_2 r c t} \;\leq\; 1 \qquad \forall\, p \in P,\; r \in R$$

where the sum is restricted to pairs that include player $p$.

**C2 — Exactly one pair per team slot per game**

$$\sum_{(p_1,p_2) \in \mathcal{P}} x_{p_1 p_2 r c t} \;=\; 1 \qquad \forall\, r \in R,\; c \in C,\; t \in T$$

**C3 — Avoidance**

$$x_{p_1 p_2 r c t} \;=\; 0 \qquad \forall\, (p_1, p_2) \in A,\; r \in R,\; c \in C,\; t \in T$$

**C4 — No two consecutive breaks**

$$z_{p r} + z_{p,r+1} \;\geq\; 1 \qquad \forall\, p \in P,\; r \in \{0, \ldots, R_{\max}-2\} : \{r, r+1\} \subseteq \text{avail}_p$$

Only enforced across rounds the player is available for — an unavailable round is an absence, not a break, and breaks the chain.

**C4a — Availability**

$$z_{p r} \;=\; 0 \qquad \forall\, p \in P,\; r \in R \setminus \text{avail}_p$$

**C4b — Required rounds**

$$z_{p r} \;=\; 1 \qquad \forall\, p \in P,\; r \in \text{req}_p$$

**C5 — Members play at least as many games as casuals**

$$\sum_{(p_1,p_2) \in \mathcal{P}} \sum_{r \in R} \sum_{c \in C} \sum_{t \in T} x_{p_1 p_2 r c t} \;\geq\; \sum_{(p_1,p_2) \in \mathcal{P}} \sum_{r \in R} \sum_{c \in C} \sum_{t \in T} x_{p_1 p_2 r c t}$$

$$\qquad \forall\, p_m \in P_M,\; p_k \in P_K$$

where each sum is restricted to pairs that include the respective player.

## Auxiliary Variable Definitions

**$z_{pr}$ definition**

$$z_{p r} \;=\; \sum_{\substack{(p_1,p_2) \in \mathcal{P} \\ p \in \{p_1,p_2\}}} \sum_{c \in C} \sum_{t \in T} x_{p_1 p_2 r c t} \qquad \forall\, p \in P,\; r \in R$$

**$\text{consec3}_{pr}$ definition** (linearised indicator)

$$\text{consec3}_{p r} \;\geq\; z_{p r} + z_{p,r+1} + z_{p,r+2} - 2 \qquad \forall\, p \in P \setminus P_{\bar{c}},\; r \in \{0, \ldots, R_{\max}-3\}$$

Players in $P_{\bar{c}}$ have no $\text{consec3}$ variable and contribute nothing to $f_{\text{consec}}$, so long streaks are unpenalised for them.

**$M$ and $m$ definitions**

$$M \;\geq\; \sum_{(p_1,p_2) \in \mathcal{P}} \sum_{r \in R} \sum_{c \in C} \sum_{t \in T} x_{p_1 p_2 r c t} \qquad \forall\, p \in P$$

$$m \;\leq\; \sum_{(p_1,p_2) \in \mathcal{P}} \sum_{r \in R} \sum_{c \in C} \sum_{t \in T} x_{p_1 p_2 r c t} \qquad \forall\, p \in P$$

**$w_{p_1 p_2}$ definition**

$$w_{p_1 p_2} \;\leq\; \sum_{r \in R} \sum_{c \in C} \sum_{t \in T} x_{p_1 p_2 r c t} \qquad \forall\, (p_1, p_2) \in \mathcal{P} \setminus A$$

**$\text{diff}_{rc}$ definition** (absolute value linearisation)

$$\text{diff}_{rc} \;\geq\; \sum_{(p_1,p_2) \in \mathcal{P}} s_{p_1 p_2}\, x_{p_1 p_2 r c 0} \;-\; \sum_{(p_1,p_2) \in \mathcal{P}} s_{p_1 p_2}\, x_{p_1 p_2 r c 1} \qquad \forall\, r \in R,\; c \in C$$

$$\text{diff}_{rc} \;\geq\; \sum_{(p_1,p_2) \in \mathcal{P}} s_{p_1 p_2}\, x_{p_1 p_2 r c 1} \;-\; \sum_{(p_1,p_2) \in \mathcal{P}} s_{p_1 p_2}\, x_{p_1 p_2 r c 0} \qquad \forall\, r \in R,\; c \in C$$

## Symmetry-Breaking Constraints

Let $\text{idx}(p_1, p_2)$ denote the index of pair $(p_1, p_2)$ in the ordered list $\mathcal{P}$.

**Team label ordering** — team 0 always holds the lower-indexed pair:

$$\sum_{(p_1,p_2) \in \mathcal{P}} \text{idx}(p_1,p_2)\cdot x_{p_1 p_2 r c 0} \;\leq\; \sum_{(p_1,p_2) \in \mathcal{P}} \text{idx}(p_1,p_2)\cdot x_{p_1 p_2 r c 1} \qquad \forall\, r \in R,\; c \in C$$

**Court ordering** — courts are ordered by their team-0 pair index within each round:

$$\sum_{(p_1,p_2) \in \mathcal{P}} \text{idx}(p_1,p_2)\cdot x_{p_1 p_2 r c 0} \;\leq\; \sum_{(p_1,p_2) \in \mathcal{P}} \text{idx}(p_1,p_2)\cdot x_{p_1 p_2 r,c+1,0} \qquad \forall\, r \in R,\; c \in \{0,\ldots,C_{\max}-2\}$$

## Objective

Maximise the weighted sum:

$$\max \quad \alpha_1 \cdot f_{\text{pref}} + \alpha_2 \cdot f_{\text{variety}} + \alpha_3 \cdot f_{\text{equality}} + \alpha_4 \cdot f_{\text{consec}} + \alpha_5 \cdot f_{\text{skill}}$$

where:

$$f_{\text{pref}} = \sum_{(p_1,p_2) \in \mathcal{P}} \sum_{r \in R} \sum_{c \in C} \sum_{t \in T} \tfrac{1}{2}\bigl(\text{pref}(p_1, p_2) + \text{pref}(p_2, p_1)\bigr)\, x_{p_1 p_2 r c t}$$

The two players' preferences for each other are **averaged**, not summed, so a mutually-preferred pair is not scored twice.

$$f_{\text{variety}} = \sum_{(p_1,p_2) \in \mathcal{P} \setminus A} w_{p_1 p_2}$$

$$f_{\text{equality}} = -(M - m) = m - M$$

$$f_{\text{consec}} = -\sum_{p \in P \setminus P_{\bar{c}}} \sum_{r=0}^{R_{\max}-3} \text{consec3}_{p r}$$

$$f_{\text{skill}} = -\sum_{r \in R} \sum_{c \in C} \text{diff}_{r c}$$

All terms are scaled to a common integer unit before being combined.
