------------------------------------------------------------------------
Onditi, KO. | Kenneth Otieno Onditi | Kenneth Onditi
------------------------------------------------------------------------
## This is a personal website on my academic profile, research interests, and professional activities. It also aims to facilitate collaborations.
------------------------------------------------------------------------
I am a molecular ecologist and evolutionary biologist, focusing on: - Small mammals (particularly rodents and shrews).
- Phylogenetics and species taxonomy.
- Biodiversity and the impacts of climate and anthropic gradients.
- ### I’m fascinated by species' adaptability to not die!
------------------------------------------------------------------------

## What You’ll Find Here

-   **Research Projects**: Explore my ongoing and completed projects.
-   **Publications**: A comprehensive list of my peer-reviewed articles.
-   **Teaching and Mentorship**: Insights into my role as a mentor for graduate students and my teaching experiences.
-   **Collaborations**: Opportunities to work with me on exciting projects.

## Feel free to reach out!🌟
------------------------------------------------------------------------


#
#
# Playground
# [Game theory]{.underline}

### 1. **Dominant Strategy:**  Always leads to the best possible outcome, regardless of the opponent's actions.

-   A strategy $s_1^*$ for Player 1 is **dominant** if: $$
    u_1(s_1^*, s_2) \geq u_1(s_1, s_2) \quad \text{for all } s_2 \in S_2, \quad \forall s_1 \in S_1
    $$
    -   Where $u_1$ is the payoff function for Player 1, and $s_1$ and $s_2$ are the strategies chosen by Player 1 and Player 2, respectively.

### 2. **Nash Equilibrium: A** stable state where everyone is making the best choice they can, given what the others are doing - no player can improve their outcome by changing their strategy while the other players keep theirs unchanged.

-   A strategy profile $(s_1^*, s_2^*)$ is a **Nash Equilibrium** if: $$
    u_1(s_1^*, s_2^*) \geq u_1(s_1, s_2^*) \quad \text{for all } s_1 \in S_1
    $$ $$
    u_2(s_1^*, s_2^*) \geq u_2(s_1^*, s_2) \quad \text{for all } s_2 \in S_2
    $$
    -   Where $u_1$ and $u_2$ are the payoffs for Player 1 and Player 2, respectively.

### 3. **Mixed Strategy: A** player randomizes their choices over several possible strategies, assigning a probability to each one. Used when there’s no clear dominant strategy, or when a player wants to make their actions less predictable.

-   For Player 1, the probability of choosing strategy $s_1^i$ is $p_1(s_1^i)$, and for Player 2, it’s $p_2(s_2^j)$.

The **expected payoff** for Player 1 and Player 2 is: $$
E(u_1) = \sum_{i=1}^{n_1} \sum_{j=1}^{n_2} p_1(s_1^i) p_2(s_2^j) u_1^i
$$ $$
E(u_2) = \sum_{i=1}^{n_1} \sum_{j=1}^{n_2} p_1(s_1^i) p_2(s_2^j) u_2^j
$$ - Where $p_1(s_1^i)$ and $p_2(s_2^j)$ are the probabilities of choosing strategies $s_1^i$ and $s_2^j$, and $u_1^i$, $u_2^j$ are the respective payoffs.

### 4. **Zero-Sum Game: O**ne in which one player's gain is exactly balanced by the other player's loss. The total amount of benefit or payoff available is fixed, and what one player wins, the other loses.

For a **zero-sum game**, the sum of the payoffs for all players equals zero: $$
u_1 + u_2 = 0
$$ - Where $u_1$ is the payoff for Player 1, and $u_2$ is the payoff for Player 2.

### 5. **Cooperative Strategy: P**layers working together, often through binding agreements, to achieve a better collective outcome. This is common in games where the players can negotiate and form coalitions.

-   In cooperative games, the focus is on **coalitions**.
    The total utility for a coalition $C \subseteq N$ of players is denoted as $v(C)$.

-   The **Shapley value** is a way to distribute the total utility $v(N)$ among the players, and it’s calculated as: $$
    \phi_i(v) = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|!(|N| - |S| - 1)!}{|N|!} [v(S \cup \{i\}) - v(S)]
    $$

    -   Where $\phi_i(v)$ is the Shapley value for player $i$, and $v(S)$ is the total utility of coalition $S$.

### 6. **Evolutionary Game Theory: P**layers are typically organisms or species that compete for survival. The strategies are the behaviors or traits of these organisms, and they evolve over time based on their fitness or reproductive success.

-   In **evolutionary stable strategies (ESS)**, a strategy $S^*$ is stable if, when most players use it, no mutant strategy $S'$ can invade and outperform it: $$
    u(S^*, S^*) > u(S', S^*) \quad \text{for all } S' \neq S^*
    $$
    -   Where $u(S^*, S^*)$ is the payoff of the strategy $S^*$ against itself, and $u(S', S^*)$ is the payoff of strategy $S'$ against $S^*$.
