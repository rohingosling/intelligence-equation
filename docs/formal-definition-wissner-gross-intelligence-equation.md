# Formal Definition of Alex Wissner-Gross's Intelligence Equation

**Author of this note:** Rohin Gosling / ChatGPT working draft  
**Subject:** Formal mathematical definition of the causal-entropic intelligence equation  
**Equation:**

$$
\mathbf{F} = T \nabla S_\tau
$$

---

## 1. Context

Alex Wissner-Gross and Cameron E. Freer proposed a thermodynamic model of adaptive behavior known as **causal entropic forces**. The central idea is that apparently intelligent behavior may emerge when a system acts so as to maximize the entropy of its accessible future histories.

The informal interpretation is:

> Intelligence-like behavior can arise from a tendency to move toward states from which many future possibilities remain accessible.

In compressed symbolic form, this idea is often written as:

$$
\mathbf{F} = T \nabla S_\tau
$$

This resembles the standard thermodynamic expression for an entropic force, but with entropy generalized from ordinary present-state entropy to **causal path entropy** over future trajectories.

---

## 2. Formal Setting

Let a physical or computational system have a configuration space:

$$
\mathcal{X}
$$

where each element

$$
\mathbf{x} \in \mathcal{X}
$$

represents a possible state or configuration of the system.

Let time be continuous or discrete. For a continuous-time formulation, define a future trajectory beginning at current state \(\mathbf{x}\) as a path:

$$
\gamma : [0, \tau] \to \mathcal{X}
$$

such that:

$$
\gamma(0) = \mathbf{x}
$$

where:

- \(\tau > 0\) is the **future time horizon**;
- \(\gamma(t)\) is the state of the system at future time \(t\);
- \(\Gamma_\tau(\mathbf{x})\) denotes the set of all dynamically admissible future paths of duration \(\tau\) starting from \(\mathbf{x}\).

Thus:

$$
\Gamma_\tau(\mathbf{x}) = \{\gamma : [0,\tau] \to \mathcal{X} \mid \gamma(0)=\mathbf{x},\ \gamma \text{ is dynamically admissible}\}
$$

---

## 3. Causal Path Entropy

The quantity \(S_\tau(\mathbf{x})\) denotes the **causal path entropy** of the future histories accessible from state \(\mathbf{x}\) over horizon \(\tau\).

In a general probabilistic formulation, suppose there is a probability measure over future paths:

$$
P(\gamma \mid \mathbf{x})
$$

for each path:

$$
\gamma \in \Gamma_\tau(\mathbf{x})
$$

Then the causal path entropy is the Shannon entropy over future paths:

$$
S_\tau(\mathbf{x})
=
- k_B \int_{\Gamma_\tau(\mathbf{x})}
P(\gamma \mid \mathbf{x})
\log P(\gamma \mid \mathbf{x})\ d\gamma
$$

where:

- \(S_\tau(\mathbf{x})\) is the entropy of accessible future paths from \(\mathbf{x}\);
- \(P(\gamma \mid \mathbf{x})\) is the probability density or probability mass assigned to future path \(\gamma\);
- \(k_B\) is Boltzmann's constant when using physical thermodynamic units;
- \(d\gamma\) denotes integration over the space of admissible future paths.

For a discrete path space, this becomes:

$$
S_\tau(\mathbf{x})
=
- k_B \sum_{\gamma \in \Gamma_\tau(\mathbf{x})}
P(\gamma \mid \mathbf{x})
\log P(\gamma \mid \mathbf{x})
$$

If all accessible future paths are treated as equally likely, and there are

$$
N_\tau(\mathbf{x}) = |\Gamma_\tau(\mathbf{x})|
$$

such paths, then:

$$
P(\gamma \mid \mathbf{x}) = \frac{1}{N_\tau(\mathbf{x})}
$$

and therefore:

$$
S_\tau(\mathbf{x}) = k_B \log N_\tau(\mathbf{x})
$$

In computational applications, the constant \(k_B\) is often omitted or absorbed into a scaling parameter, giving:

$$
S_\tau(\mathbf{x}) \propto \log N_\tau(\mathbf{x})
$$

---

## 4. The Intelligence Equation

The causal-entropic force is formally defined as:

$$
\mathbf{F}(\mathbf{x}) = T \nabla_{\mathbf{x}} S_\tau(\mathbf{x})
$$

where:

- \(\mathbf{F}(\mathbf{x})\) is the causal-entropic force acting at state \(\mathbf{x}\);
- \(T\) is a temperature-like scaling parameter;
- \(S_\tau(\mathbf{x})\) is the causal path entropy over future trajectories of duration \(\tau\);
- \(\nabla_{\mathbf{x}} S_\tau(\mathbf{x})\) is the gradient of causal path entropy with respect to the current state coordinates;
- \(\tau\) is the future time horizon over which possible future histories are evaluated.

Thus, the direction of \(\mathbf{F}\) is the direction in configuration space that most rapidly increases future path entropy.

Equivalently:

$$
\mathbf{F}(\mathbf{x})
\parallel
\nabla_{\mathbf{x}} S_\tau(\mathbf{x})
$$

and its magnitude is scaled by \(T\):

$$
\|\mathbf{F}(\mathbf{x})\|
=
T \|\nabla_{\mathbf{x}} S_\tau(\mathbf{x})\|
$$

---

## 5. Interpretation of Each Symbol

| Symbol | Meaning |
|---|---|
| \(\mathbf{F}\) | Causal-entropic force; the effective drive toward states with greater future freedom of action. |
| \(T\) | Temperature-like parameter controlling the strength of the entropic force. |
| \(\nabla\) | Gradient operator with respect to the system's current state or configuration. |
| \(S_\tau\) | Causal path entropy of possible future histories over horizon \(\tau\). |
| \(\tau\) | Future time horizon over which accessible future paths are counted or weighted. |
| \(\mathcal{X}\) | State or configuration space of the system. |
| \(\Gamma_\tau(\mathbf{x})\) | Set of admissible future paths starting at state \(\mathbf{x}\) and extending to horizon \(\tau\). |
| \(P(\gamma \mid \mathbf{x})\) | Probability of future path \(\gamma\) conditioned on current state \(\mathbf{x}\). |

---

## 6. Discrete-State Version

For a discrete turn-based system, such as a board game, let:

$$
S
$$

be a finite or countable set of states, and let:

$$
A(s)
$$

be the set of legal actions available at state \(s \in S\).

Let the transition function be:

$$
T_g : S \times A \to S
$$

where \(T_g(s,a)\) gives the next state reached after taking action \(a\) in state \(s\). The subscript \(g\) is used here to avoid confusing the game transition function \(T_g\) with the temperature-like scalar \(T\) in the intelligence equation.

For a discrete horizon \(\tau \in \mathbb{N}\), define the set of reachable future histories:

$$
\Gamma_\tau(s)
=
\{(s_0,a_0,s_1,a_1,\dots,s_\tau)
\mid
s_0=s,\ s_{i+1}=T_g(s_i,a_i),\ a_i \in A(s_i)
\}
$$

The discrete causal path entropy is:

$$
S_\tau(s)
=
- \sum_{\gamma \in \Gamma_\tau(s)}
P(\gamma \mid s) \log P(\gamma \mid s)
$$

If all reachable future histories are weighted uniformly, then:

$$
S_\tau(s) = \log |\Gamma_\tau(s)|
$$

Since discrete game states do not usually have a smooth geometry, the gradient \(\nabla S_\tau\) is replaced by a finite action-wise entropy difference:

$$
\Delta S_\tau(s,a)
=
S_\tau(T_g(s,a)) - S_\tau(s)
$$

The discrete analogue of the causal-entropic action score is then:

$$
C(s,a)
=
T \cdot \Delta S_\tau(s,a)
$$

An entropic agent may choose an action by maximizing this score:

$$
a^*(s)
=
\arg\max_{a \in A(s)} C(s,a)
$$

or equivalently:

$$
a^*(s)
=
\arg\max_{a \in A(s)} \left[ S_\tau(T_g(s,a)) - S_\tau(s) \right]
$$

Since \(S_\tau(s)\) is constant with respect to \(a\) at a fixed state \(s\), this is often equivalent to:

$$
a^*(s)
=
\arg\max_{a \in A(s)} S_\tau(T_g(s,a))
$$

However, the difference form is the more direct analogue of the gradient in the original equation.

---

## 7. Relation to Intelligent Behavior

The equation says that an agent-like system is driven toward states with greater future freedom of action.

More explicitly, an action is favored when it increases:

- the number of reachable future states;
- the diversity of reachable future trajectories;
- the system's ability to avoid constraint, trap states, or premature commitment;
- the entropy of possible future histories over the horizon \(\tau\).

Thus, the principle is not equivalent to ordinary utility maximization with a hand-coded goal. Instead, it proposes a generic pressure toward maintaining or increasing future optionality.

This is why the idea is often summarized as:

> intelligence is the tendency to maximize future freedom of action.

---

## 8. Important Caveats

The equation should be interpreted carefully.

First, \(\mathbf{F} = T \nabla S_\tau\) is not a complete theory of artificial general intelligence. It is a proposed physical principle that can generate adaptive-looking behavior in certain systems.

Second, maximizing future entropy is not always the same as winning a game, solving a problem, or achieving a human-specified objective. In a game such as Tic-tac-toe, an entropy-maximizing move may keep many future options open, but a game-winning move may sometimes deliberately reduce options by forcing a terminal win.

Third, in discrete games, the true gradient is not directly available unless the state space is embedded into a differentiable geometry. For such systems, finite differences over legal actions are the natural replacement.

Fourth, the choice of future-path probability distribution \(P(\gamma \mid s)\) matters. Uniform counting of future paths is simple, but it may not represent realistic dynamics, strategic opponents, or physical constraints.

---

## 9. Compact Formal Definition

A compact formal definition is:

Let \(\mathcal{X}\) be a configuration space, \(\Gamma_\tau(\mathbf{x})\) the set of admissible future paths of duration \(\tau\) starting from \(\mathbf{x}\), and \(P(\gamma \mid \mathbf{x})\) a probability measure over those paths. Define causal path entropy by:

$$
S_\tau(\mathbf{x})
=
- \int_{\Gamma_\tau(\mathbf{x})}
P(\gamma \mid \mathbf{x})
\log P(\gamma \mid \mathbf{x})\ d\gamma
$$

Then the causal-entropic force is:

$$
\mathbf{F}(\mathbf{x}) = T \nabla_{\mathbf{x}} S_\tau(\mathbf{x})
$$

An intelligent or adaptive action is one that moves the system in the direction of increasing future path entropy.

---

## 10. References

- A. D. Wissner-Gross and C. E. Freer, **"Causal Entropic Forces,"** *Physical Review Letters*, 110, 168702, 2013. DOI: `10.1103/PhysRevLett.110.168702`.
- PubMed record: **"Causal entropic forces"**, PMID `23679649`.
- Related concept: ordinary thermodynamic **entropic force**, usually expressed as `F = T ∇S`, generalized here to future path entropy `S_τ`.
