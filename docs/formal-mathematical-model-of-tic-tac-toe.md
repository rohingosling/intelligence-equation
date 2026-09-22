# Formal Mathematical Model of Tic-Tac-Toe

## 1. Overview

This document defines the game of Tic-tac-toe as a finite, deterministic, two-player, turn-based, zero-sum game of perfect information.

The model uses the game tuple:

$$
G = (S, s_0, A, P, T, O, U)
$$

where:

- $S$ is the set of legal reachable game states.
- $s_0$ is the initial state.
- $A(s)$ is the set of legal actions available in state $s$.
- $P(s)$ is the player-to-move function.
- $T(s,a)$ is the transition function.
- $O(s)$ is the outcome function.
- $U_i(s)$ is the utility function for player $i$.

Tic-tac-toe is solved: under optimal play by both players, the game value from the initial state is a draw.

---

## 2. Primitive Sets

Let the board coordinates be:

$$
R = \{1,2,3\}
$$

$$
C = \{1,2,3\}
$$

The set of board cells is:

$$
D = R \times C
$$

Thus, each cell is an ordered pair:

$$
(r,c) \in D
$$

where $r$ is the row and $c$ is the column.

The set of marks is:

$$
M = \{X, O\}
$$

The symbol for an empty cell is:

$$
\emptyset
$$

The set of possible cell values is:

$$
\Sigma = \{X, O, \emptyset\}
$$

The set of players is:

$$
I = \{X, O\}
$$

For simplicity, each player is identified with their mark. Player $X$ moves first, and player $O$ moves second.

---

## 3. Board Representation

A board is a function:

$$
b : D \to \Sigma
$$

That is, a board assigns one of the values $X$, $O$, or $\emptyset$ to each cell of the $3 \times 3$ grid.

The set of all possible raw board configurations is:

$$
B = \Sigma^D
$$

Since $|D| = 9$ and $|\Sigma| = 3$, the number of raw board configurations is:

$$
|B| = 3^9 = 19683
$$

However, not every element of $B$ is a legal Tic-tac-toe position. Some boards violate turn order or contain impossible win configurations. The legal state space $S$ is therefore defined as a subset of $B$.

---

## 4. Mark Counts

For a board $b$, define the number of $X$ marks as:

$$
n_X(b) = |\{d \in D : b(d) = X\}|
$$

Define the number of $O$ marks as:

$$
n_O(b) = |\{d \in D : b(d) = O\}|
$$

Because $X$ moves first and players alternate turns, any reachable non-corrupt board must satisfy:

$$
n_X(b) = n_O(b)
$$

or

$$
n_X(b) = n_O(b) + 1
$$

Equivalently:

$$
n_X(b) \in \{n_O(b), n_O(b)+1\}
$$

---

## 5. Winning Lines

The set of all winning lines is:

$$
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
$$

There are eight winning lines:

- three rows;
- three columns;
- two diagonals.

---

## 6. Win Predicate

For a player $m \in M$, define the win predicate:

$$
W_m(b)
\iff
\exists L \in \mathcal{L}
\text{ such that }
\forall d \in L,\ b(d) = m
$$

In words: player $m$ has won on board $b$ if and only if there exists at least one winning line whose cells are all marked by $m$.

So:

$$
W_X(b)
$$

means that $X$ has a completed line, and:

$$
W_O(b)
$$

means that $O$ has a completed line.

---

## 7. Full-Board Predicate

A board is full if no cell is empty:

$$
F(b)
\iff
\forall d \in D,\ b(d) \neq \emptyset
$$

Equivalently:

$$
F(b)
\iff
n_X(b) + n_O(b) = 9
$$

---

## 8. Terminal Predicate

A board is terminal if either player has won or the board is full:

$$
Z(b)
\iff
W_X(b) \lor W_O(b) \lor F(b)
$$

A non-terminal board is one for which:

$$
\neg Z(b)
$$

---

## 9. Legal State Space

The legal state space $S$ is the set of all boards reachable from the empty board by a finite sequence of legal moves, stopping immediately when a terminal state is reached.

The initial board $s_0$ is the empty board:

$$
s_0(d) = \emptyset
\quad
\forall d \in D
$$

The legal state space is defined recursively as the smallest set $S \subseteq B$ such that:

1. The initial state is legal:

$$
s_0 \in S
$$

2. If $s \in S$, $s$ is non-terminal, and $a \in A(s)$, then:

$$
T(s,a) \in S
$$

3. No successors are generated from terminal states:

$$
Z(s) \implies A(s) = \varnothing
$$

This recursive definition is preferable to merely specifying count constraints, because it excludes positions that could not arise under actual game play.

---

## 10. Player-to-Move Function

The player-to-move function is:

$$
P : S \setminus Z \to I
$$

where $Z$ denotes the set of terminal states.

Since $X$ moves first:

$$
P(s)
=
\begin{cases}
X, & \text{if } n_X(s) = n_O(s), \\
O, & \text{if } n_X(s) = n_O(s) + 1.
\end{cases}
$$

The function $P(s)$ is undefined for terminal states, because no player moves after the game has ended.

---

## 11. Action Set

An action is the selection of an empty board cell:

$$
a \in D
$$

For a non-terminal state $s$, the legal action set is:

$$
A(s)
=
\{d \in D : s(d) = \emptyset\}
$$

For a terminal state $s$, no actions are legal:

$$
Z(s) \implies A(s) = \varnothing
$$

Thus, in Tic-tac-toe, an action does not need to explicitly contain the player's mark. The mark is determined by the player-to-move function $P(s)$.

---

## 12. Transition Function

The transition function is:

$$
T : S \times D \to S
$$

For a state $s \in S$ and legal action $a \in A(s)$, the successor state $s' = T(s,a)$ is defined by:

$$
s'(d)
=
\begin{cases}
P(s), & \text{if } d = a, \\
s(d), & \text{otherwise}.
\end{cases}
$$

In words: the current player places their mark in the selected empty cell, and all other cells remain unchanged.

The transition function is only defined when:

$$
a \in A(s)
$$

and:

$$
\neg Z(s)
$$

---

## 13. Outcome Function

The outcome function is:

$$
O : S \to \{\text{X-wins}, \text{O-wins}, \text{Draw}, \text{Ongoing}\}
$$

It is defined as:

$$
O(s)
=
\begin{cases}
\text{X-wins}, & \text{if } W_X(s), \\
\text{O-wins}, & \text{if } W_O(s), \\
\text{Draw}, & \text{if } F(s) \land \neg W_X(s) \land \neg W_O(s), \\
\text{Ongoing}, & \text{otherwise}.
\end{cases}
$$

Because the legal state space is defined by reachable game play, a legal terminal state should not require moves after a win has already occurred.

---

## 14. Utility Functions

Define utility functions:

$$
U_X : S \to \{-1,0,1\}
$$

$$
U_O : S \to \{-1,0,1\}
$$

For player $X$:

$$
U_X(s)
=
\begin{cases}
1, & \text{if } O(s) = \text{X-wins}, \\
-1, & \text{if } O(s) = \text{O-wins}, \\
0, & \text{if } O(s) = \text{Draw}, \\
0, & \text{if } O(s) = \text{Ongoing}.
\end{cases}
$$

For player $O$:

$$
U_O(s)
=
\begin{cases}
1, & \text{if } O(s) = \text{O-wins}, \\
-1, & \text{if } O(s) = \text{X-wins}, \\
0, & \text{if } O(s) = \text{Draw}, \\
0, & \text{if } O(s) = \text{Ongoing}.
\end{cases}
$$

For terminal states, Tic-tac-toe is zero-sum:

$$
U_X(s) = -U_O(s)
$$

for every terminal state $s$.

---

## 15. Histories

A history is a finite sequence of actions:

$$
h = (a_1, a_2, \dots, a_k)
$$

where each action is legal at the state in which it is played.

The state induced by a history is defined recursively:

$$
s_h =
T(
  T(
    \dots
      T(s_0,a_1),
    a_2
  ),
  \dots,
  a_k
)
$$

provided every transition is legal.

The length of a history is:

$$
|h| = k
$$

For any reachable state $s_h$:

$$
n_X(s_h) + n_O(s_h) = |h|
$$

---

## 16. Strategies

A pure strategy for player $i \in I$ is a function:

$$
\sigma_i : S_i \to D
$$

where:

$$
S_i = \{s \in S : P(s) = i\}
$$

and:

$$
\sigma_i(s) \in A(s)
$$

for every state $s \in S_i$.

In words: a strategy tells a player which legal action to take in every state where it is that player's turn.

A strategy profile is:

$$
\sigma = (\sigma_X, \sigma_O)
$$

Given a strategy profile and the initial state $s_0$, the play sequence is fully determined because Tic-tac-toe is deterministic and has perfect information.

---

## 17. Minimax Value Function

For player $X$, define the minimax value function:

$$
V_X : S \to \{-1,0,1\}
$$

For terminal states:

$$
V_X(s) = U_X(s)
$$

For non-terminal states:

$$
V_X(s)
=
\begin{cases}
\max\limits_{a \in A(s)} V_X(T(s,a)), & \text{if } P(s) = X, \\
\min\limits_{a \in A(s)} V_X(T(s,a)), & \text{if } P(s) = O.
\end{cases}
$$

Similarly, for player $O$:

$$
V_O(s) = -V_X(s)
$$

because the game is zero-sum.

The optimal action for $X$ in state $s$ is:

$$
a_X^*(s)
\in
\arg\max_{a \in A(s)} V_X(T(s,a))
$$

The optimal action for $O$ in state $s$ is:

$$
a_O^*(s)
\in
\arg\min_{a \in A(s)} V_X(T(s,a))
$$

Equivalently, from $O$'s own perspective:

$$
a_O^*(s)
\in
\arg\max_{a \in A(s)} V_O(T(s,a))
$$

---

## 18. Value of the Initial State

The value of the initial Tic-tac-toe state is:

$$
V_X(s_0) = 0
$$

Therefore, under optimal play:

$$
O(s_{\text{final}}) = \text{Draw}
$$

This means that neither player can force a win if both players play optimally.

---

## 19. Compact Final Definition

The formal Tic-tac-toe game is:

$$
G_{\text{TTT}}
=
(S, s_0, A, P, T, O, U)
$$

with:

$$
D = \{1,2,3\} \times \{1,2,3\}
$$

$$
\Sigma = \{X,O,\emptyset\}
$$

$$
S \subseteq \Sigma^D
$$

where $S$ is the recursively reachable legal state space from $s_0$.

The initial state is:

$$
s_0(d) = \emptyset
\quad
\forall d \in D
$$

The player-to-move function is:

$$
P(s)
=
\begin{cases}
X, & n_X(s) = n_O(s), \\
O, & n_X(s) = n_O(s)+1.
\end{cases}
$$

The legal action function is:

$$
A(s)
=
\{d \in D : s(d) = \emptyset\}
$$

for non-terminal states, and:

$$
A(s)=\varnothing
$$

for terminal states.

The transition function is:

$$
T(s,a)(d)
=
\begin{cases}
P(s), & d=a, \\
s(d), & d \neq a.
\end{cases}
$$

The outcome function is:

$$
O(s)
=
\begin{cases}
\text{X-wins}, & W_X(s), \\
\text{O-wins}, & W_O(s), \\
\text{Draw}, & F(s) \land \neg W_X(s) \land \neg W_O(s), \\
\text{Ongoing}, & \text{otherwise}.
\end{cases}
$$

The utilities are:

$$
U_X(s)
=
\begin{cases}
1, & O(s)=\text{X-wins}, \\
-1, & O(s)=\text{O-wins}, \\
0, & O(s)=\text{Draw}.
\end{cases}
$$

and:

$$
U_O(s) = -U_X(s)
$$

for terminal states.

Finally, the minimax value from the initial state is:

$$
V_X(s_0)=0
$$

so optimal play results in a draw.

---

## 20. Notes on Implementation Mapping

The mathematical model maps naturally into an object-oriented implementation:

- $S$ corresponds to a `State` class.
- $s_0$ corresponds to the initial empty `State`.
- The board function $b : D \to \Sigma$ corresponds to a `Board` class.
- $A(s)$ corresponds to `get_possible_actions()`.
- $P(s)$ corresponds to the current-player or player-to-move logic.
- $T(s,a)$ corresponds to `apply_action(action)`.
- $O(s)$ corresponds to outcome detection such as `check_win()` and draw detection.
- $U_i(s)$ corresponds to a utility or cost function.
- $V_i(s)$ corresponds to minimax evaluation.
