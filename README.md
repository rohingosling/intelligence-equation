# Playing Tic-Tac-Toe with Causal-Entropy, $\mathbf{F} = T \nabla S_\tau$

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PyYAML](https://img.shields.io/badge/PyYAML-6.x-CB171E?style=flat&logo=yaml&logoColor=white)](https://pyyaml.org/)
[![Rich](https://img.shields.io/badge/Rich-15.x-FFDD00?style=flat)](https://rich.readthedocs.io/)

<p align="center">
  <img src="images\Screenshot-computer-vs-computer-2.png" width="100%" alt="Computer-versus-computer Tic-tac-toe match in the terminal">&emsp;
</p>

A Tic-tac-toe sandbox to experiment with Alex Wissner-Gross's causal-entropic intelligence equation.

```math
\mathbf{F} = T \nabla S_\tau
```

<br>

In this application, the causal-entropy player treats each legal Tic-tac-toe move as a step into a future game tree.
As defined by $\mathbf{F} = T \nabla S_\tau$, it prefers moves whose successor states leave many legal future histories available, instead of directly optimizing a win/loss utility score. For this reason we observe that the causal-entropy favours placing marks on the edges of the board to minimise the probability of loosing, in favour of dominating the center to maximise the probability of winning.

*...Basicaly, the agent that avoids loosing, lives longer, than the agent that tries to win.*<br>
*...There may be some philisophical value in that observation somewhere.*

<br>

<a id="table-of-contents"></a>

## 📋 Table of Contents

- [✅ Requirements](#requirements)
- [⚙️ Setup](#setup)
- [▶️ Running](#running)
- [🧩 Configuration](#configuration)
- [🧮 Mathematical Overview](#mathematical-overview)
- [🎮 Tic-tac-toe - Mathematical Definition](#tic-tac-toe-mathematical-definition)
- [🗂️ Project Layout](#project-layout)
- [⚠️ Experiment Limitations](#experiment-limitations)
- [📜 License](#license)

<br>

<a id="requirements"></a>

## ✅ Requirements

- Python 3.12 or newer
- A UTF-8 terminal for Unicode boards; other encodings receive an ASCII fallback

<br>

<a id="setup"></a>

## ⚙️ Setup

Create a virtual environment, then install the dependencies.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Linux or macOS

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

### Windows Git Bash

```bash
py -3.12 -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Use `requirements-dev.txt` only when you want the optional local test dependencies.

<br>

<a id="running"></a>

## ▶️ Running

From the project directory, display the available command-line options:

- **Windows**

  ```powershell
  .\run.bat --help
  ```

- **Linux**

  ```bash
  ./run.sh --help
  ```

Run the example causal-entropy match:

- **Windows**

  ```powershell
  .\run.bat config\example.yaml
  ```

- **Linux**

  ```bash
  ./run.sh config/example.yaml
  ```

Run a causal-entropy versus minimax experiment with candidate-score diagnostics:

- **Windows**

  ```powershell
  .\run.bat config\experiments\causal-entropy-x-minimax-o.yaml
  ```

- **Linux**

  ```bash
  ./run.sh config/experiments/causal-entropy-x-minimax-o.yaml
  ```

The selected YAML profiles determine whether a match is human-human, human-computer, or computer-computer. Human
turns accept coordinates from `a1` through `c3`; malformed and occupied coordinates are explained and re-prompted.

<br>

<a id="configuration"></a>

## 🧩 Configuration

Each YAML file defines an `x.y` version number, optional application settings, reusable player profiles, one selected
match, and presentation settings. An integer `application.random_seed` makes random strategy choices and random tie-breaks
repeatable; omit it or set it to `null` for fresh random initialization on each run.

| Match profiles | Play mode |
|---|---|
| Human + human | Human versus human |
| Human + computer | Human versus computer |
| Computer + computer | Computer versus computer |

Player 1 is always `X` and moves first. Computer profiles select one of these strategies:

| Strategy | Behavior |
|---|---|
| `random` | Uniform choice from legal actions |
| `tactical` | Win, block, center, corner, then edge |
| `minimax` | Complete optimal search using terminal utility |
| `causal_entropy` | Maximizes future-history entropy without utility or tactical bonuses |

The included files under `config/` show the supported profile, match, and presentation settings.

<br>

<a id="mathematical-overview"></a>

## 🧮 Mathematical Overview

Wissner-Gross's causal-entropic force,

```math
\mathbf{F} = T \nabla S_\tau
```

says that a system is driven toward states with greater future path entropy. Tic-tac-toe is discrete, so the
application replaces the smooth gradient with an action-wise finite difference over legal moves.

Let $s$ be the current Tic-tac-toe state, $A(s)$ the legal actions, and $T_g(s,a)$ the successor state reached by
playing action $a$. The subscript in $T_g$ distinguishes the game transition function from the temperature-like
scalar $T$ in the intelligence equation. The formal Tic-tac-toe definition below uses $T$ for the same game
transition function, matching the notation in the reference model.

For a configured horizon $\tau$, the causal-entropy strategy counts uniformly weighted future histories:

```math
N_0(s) = 1
```

```math
N_\tau(s) =
\begin{cases}
1, & \text{if } s \text{ is terminal}, \\
\sum\limits_{a \in A(s)} N_{\tau - 1}(T_g(s,a)), & \text{otherwise}.
\end{cases}
```

The path entropy used by the application is the natural logarithm of that count:

```math
S_\tau(s) = \log N_\tau(s)
```

Each candidate move is scored by the discrete analogue of $T \nabla S_\tau$:

```math
C(s,a) =
\theta \left[S_\tau(T_g(s,a)) - S_\tau(s)\right]
```

where $\theta$ is the configured `temperature` parameter. Since $S_\tau(s)$ is constant for all candidate moves
from the same state, choosing the largest $C(s,a)$ is equivalent to choosing the successor with the largest future
path entropy.

The strategy intentionally does not add win/loss utility, tactical rules, or an opponent model. Wins, losses, and
draws affect the score only by ending the future-history count. This makes the causal-entropy player a direct test of
future optionality inside the Tic-tac-toe game defined below.

<br>

<a id="tic-tac-toe-mathematical-definition"></a>

## 🎮 Tic-tac-toe - Mathematical Definition

Tic-tac-toe is modeled as a finite, deterministic, two-player, turn-based, zero-sum game of perfect information:

```math
G = (S, s_0, A, P, T, O, U)
```

where $S$ is the legal reachable state space, $s_0$ is the initial state, $A(s)$ is the legal action function,
$P(s)$ is the player-to-move function, $T(s,a)$ is the transition function, $O(s)$ is the outcome function, and
$U_i(s)$ is the utility function for player $i$.

Let the row and column sets be:

```math
R = \{1,2,3\}
```

```math
C = \{1,2,3\}
```

The set of board cells is:

```math
D = R \times C
```

The marks are:

```math
M = \{X, O\}
```

The empty cell symbol is $\emptyset$, and the set of possible cell values is:

```math
\Sigma = \{X, O, \emptyset\}
```

The set of players is:

```math
I = \{X, O\}
```

Each player is identified with their mark. Player $X$ moves first, and player $O$ moves second.

A board is a function:

```math
b : D \to \Sigma
```

The raw board space is:

```math
B = \Sigma^D
```

Since $|D| = 9$ and $|\Sigma| = 3$, there are $|B| = 3^9 = 19683$ raw board configurations. The legal state space
$S$ is a subset of $B$ because some raw boards violate turn order or could not arise after normal play.

For a board $b$, define the mark counts:

```math
n_X(b) = |\{d \in D : b(d) = X\}|
```

```math
n_O(b) = |\{d \in D : b(d) = O\}|
```

Because $X$ moves first and players alternate turns, every reachable non-corrupt board satisfies:

```math
n_X(b) = n_O(b)
```

or:

```math
n_X(b) = n_O(b) + 1
```

Equivalently:

```math
n_X(b) \in \{n_O(b), n_O(b)+1\}
```

The set of winning lines is:

```math
\mathcal{L}
=
\left\{
\begin{aligned}
&\{(1,1),(1,2),(1,3)\}, \\
&\{(2,1),(2,2),(2,3)\}, \\
&\{(3,1),(3,2),(3,3)\}, \\
&\{(1,1),(2,1),(3,1)\}, \\
&\{(1,2),(2,2),(3,2)\}, \\
&\{(1,3),(2,3),(3,3)\}, \\
&\{(1,1),(2,2),(3,3)\}, \\
&\{(1,3),(2,2),(3,1)\}
\end{aligned}
\right\}
```

For a player $m \in M$, the win predicate is:

```math
W_m(b)
\iff
\exists L \in \mathcal{L}
\text{ such that }
\forall d \in L,\ b(d) = m
```

A board is full if no cell is empty:

```math
F(b)
\iff
\forall d \in D,\ b(d) \neq \emptyset
```

Equivalently:

```math
F(b)
\iff
n_X(b) + n_O(b) = 9
```

A board is terminal if either player has won or the board is full:

```math
Z(b)
\iff
W_X(b) \lor W_O(b) \lor F(b)
```

The initial state $s_0$ is the empty board:

```math
s_0(d) = \emptyset
\quad
\forall d \in D
```

The legal state space is the smallest set $S \subseteq B$ such that:

1. $s_0 \in S$.
2. If $s \in S$, $s$ is non-terminal, and $a \in A(s)$, then $T(s,a) \in S$.
3. If $Z(s)$, then $A(s) = \varnothing$.

This recursive definition excludes boards that satisfy simple count constraints but could not arise during actual
game play.

For non-terminal states, the player-to-move function is:

```math
P(s) =
\begin{cases}
X, & \text{if } n_X(s) = n_O(s), \\
O, & \text{if } n_X(s) = n_O(s) + 1.
\end{cases}
```

The function $P(s)$ is undefined for terminal states because no player moves after the game ends.

An action is the selection of an empty board cell:

```math
a \in D
```

The legal action set is the set of empty cells:

```math
A(s)
=
\{d \in D : s(d) = \emptyset\}
```

For terminal states, no actions are legal:

```math
Z(s) \implies A(s) = \varnothing
```

For a state $s \in S$ and legal action $a \in A(s)$, the successor state $s' = T(s,a)$ is:

```math
s'(d)
=
\begin{cases}
P(s), & \text{if } d = a, \\
s(d), & \text{otherwise}.
\end{cases}
```

The transition function is only defined when $a \in A(s)$ and $\neg Z(s)$.

The outcome function is:

```math
O : S \to \{\text{X-wins}, \text{O-wins}, \text{Draw}, \text{Ongoing}\}
```

with:

```math
O(s) =
\begin{cases}
\text{X-wins}, & \text{if } W_X(s), \\
\text{O-wins}, & \text{if } W_O(s), \\
\text{Draw}, & \text{if } F(s) \land \neg W_X(s) \land \neg W_O(s), \\
\text{Ongoing}, & \text{otherwise}.
\end{cases}
```

The utility functions are:

```math
U_X : S \to \{-1,0,1\}
```

```math
U_O : S \to \{-1,0,1\}
```

For player $X$:

```math
U_X(s) =
\begin{cases}
1, & \text{if } O(s) = \text{X-wins}, \\
-1, & \text{if } O(s) = \text{O-wins}, \\
0, & \text{if } O(s) = \text{Draw}, \\
0, & \text{if } O(s) = \text{Ongoing}.
\end{cases}
```

For player $O$:

```math
U_O(s) =
\begin{cases}
1, & \text{if } O(s) = \text{O-wins}, \\
-1, & \text{if } O(s) = \text{X-wins}, \\
0, & \text{if } O(s) = \text{Draw}, \\
0, & \text{if } O(s) = \text{Ongoing}.
\end{cases}
```

For terminal states, Tic-tac-toe is zero-sum:

```math
U_X(s) = -U_O(s)
```

A history is a finite legal action sequence:

```math
h = (a_1, a_2, \dots, a_k)
```

The induced state $s_h$ is obtained by applying those actions in order from $s_0$, and:

```math
n_X(s_h) + n_O(s_h) = |h|
```

A pure strategy for player $i \in I$ maps every state where that player moves to a legal action:

```math
\sigma_i : S_i \to D
```

where:

```math
S_i = \{s \in S : P(s) = i\}
```

and:

```math
\sigma_i(s) \in A(s)
```

For player $X$, the minimax value function is:

```math
V_X : S \to \{-1,0,1\}
```

with:

```math
V_X(s) = U_X(s)
```

for terminal states, and:

```math
V_X(s)
=
\begin{cases}
\max\limits_{a \in A(s)} V_X(T(s,a)), & \text{if } P(s) = X, \\
\min\limits_{a \in A(s)} V_X(T(s,a)), & \text{if } P(s) = O.
\end{cases}
```

Similarly, $V_O(s) = -V_X(s)$ because the game is zero-sum. Tic-tac-toe is solved: the value of the initial state is:

```math
V_X(s_0)=0
```

so optimal play results in a draw.

<br>

<a id="project-layout"></a>

## 🗂️ Project Layout

| Path | Responsibility |
|---|---|
| `domain/` | Immutable board, state, outcomes, coordinates, and authoritative game rules |
| `players/` | Human and computer player abstractions |
| `intelligence/` | Interchangeable computer strategies |
| `presentation/` | Terminal rendering and interaction |
| `config/` | Example and experiment YAML configurations |
| `docs/` | Architecture notes, experiment baseline, and mathematical models |
| `main.py` | Minimal executable entry point |
| `run.bat`, `run.sh` | Windows and Linux terminal launchers |
| `application.py` | Application composition and lifecycle |
| `configuration.py` | Typed YAML loading and aggregated validation |
| `errors.py` | Shared application exception types |

<br>

<a id="experiment-limitations"></a>

## ⚠️ Experiment Limitations

- Each example result is one seeded game, not a statistical comparison.
- In matches with random strategies or random tie-breakers, role assignment affects how the shared seeded random stream is consumed.
- Execution times are machine-specific and are not acceptance thresholds.
- The causal-entropy strategy intentionally ignores wins, losses, and opponent quality except through future path
  counts.
- Tic-tac-toe is a small demonstration domain; these results do not establish a general measure of intelligence.

<br>

<a id="license"></a>

## 📜 License

Released under the [MIT License](LICENSE) — Copyright © 2022 Rohin Gosling.
