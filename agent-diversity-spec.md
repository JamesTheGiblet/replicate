# 🧬 Replicant Agent Diversity Framework Spec

**Version: 0.1**  
**Status: Proposed**

---

## 1. Philosophy: Beyond Handedness

The current `is_specialist` trait is a crucial first step, analogous to left-handedness in humans. It creates a persistent minority that breaks symmetry and prevents "thundering herd" role collapse.

However, true swarm intelligence and resilience emerge from a deeper, more nuanced diversity. Human diversity isn't just about handedness; it's a spectrum of personalities, cognitive biases, risk tolerances, and worldviews. A society of pure conformists is brittle; a society of pure contrarians is chaotic. The most resilient systems blend these perspectives.

This document proposes a framework for evolving the Replicant agent model from a binary system (generalist/specialist) to a richer spectrum of **Agent Archetypes**.

---

## 2. The Problem: The Limits of a Homogeneous Mindset

A swarm where every agent, specialist or not, uses the same core evaluation logic is still a monoculture of thought.

- **Reactive vs. Proactive:** Generalists are purely reactive, filling the most immediate need. This is vital for short-term stability but can miss long-term opportunities or threats.
- **Brittleness:** If the logic for identifying "needs" is flawed or can be exploited, the entire swarm is vulnerable.
- **Lost Potential:** Agents have a diverse set of `Traits` (scepticism, forage_bias), but these are currently used as minor weights in a single decision tree. They could be the foundation of entirely different cognitive models.

---

## 3. Proposed Framework: Agent Archetypes

We will replace the `is_specialist: bool` with an `archetype: Archetype` enum, assigned at birth and immutable. This archetype will dictate the agent's core "philosophy" for decision-making, especially concerning role selection.

### 3.1. Initial Archetypes

These archetypes are defined by how they prioritize information—internal traits, external swarm state, or global task priorities.

| Archetype | Population | Decision Driver | Description |
|---|---|---|---|
| **Generalist** | ~60% | **Swarm Task Priorities (Global)** | The reliable majority. They dynamically assess global swarm needs and adopt roles to fulfill the most critical tasks, ensuring the "unified organism" functions effectively. They are reactive and essential for collective homeostasis. |
| **Purist** | ~10% | **Innate Traits (Internal)** | The true specialists. They largely ignore immediate swarm needs and adopt the role that best fits their "personality" (highest traits). A high-scepticism Purist *will* become an Attester. They are the guardians of specialized knowledge. |
| **Contrarian** | ~10% | **Inverse Swarm Needs (Local/Global)** | This archetype actively seeks to fill the *least* common role, either locally or globally. If the swarm is 90% Foragers, the Contrarian is drawn to becoming a Builder or Observer. They are a powerful, built-in mechanism against monoculture and for exploring new strategies. |
| **Opportunist** | ~5% | **Highest Reward (Internal/Historical)** | This agent tracks its own `recent_reward` and develops an affinity for roles that have been most profitable *for it personally*. It introduces a simple learning mechanism, potentially discovering new efficiencies. |
| **Historian** | ~5% | **Pattern Analysis (Historical)** | A rare, highly specialized role. Historians analyze their personal `chronicle` and the public claim network to identify long-term patterns. They generate `CONTEXT` claims—meta-claims about the system's behavior. |
| **Messenger** | ~5% | **Information Gradient** | Travels to information-sparse regions of the map, "collects" knowledge of isolated or old claims, and returns to high-density areas to "re-broadcast" them, preventing valuable knowledge from being forgotten. They are the swarm's long-range information couriers. |
| **Gamewright**| ~<5% | **Pattern Formalization** | The rarest archetype. Driven by high novelty-seeking traits, it observes social patterns and attempts to formalize them into abstract games with rules and objectives, which can then spread as memes. |

### 3.2. Swarm Task Priority System

To enable the "unified organism" behavior, the `World` will calculate and expose a set of global `SwarmTaskPriorities` each tick. These priorities will represent the overall health and needs of the swarm, allowing Generalist agents to make informed decisions about which roles are most critical for the collective.

These priorities will be added to the `Percepts` struct, making them visible to agents during their `decide()` phase.

**Example Global Task Priorities (0.0 - 1.0, higher means more needed):**

- `global_forager_need`: Based on average agent energy, total available resources, and resource depletion rates.
- `global_builder_need`: Based on the number of depleted resource patches and the overall carrying capacity.
- `global_attester_need`: Based on the ratio of `Opinion` claims to `Fact` claims, and the age of `Opinion` claims.
- `global_explorer_need`: Based on the proportion of unexplored territory or the rate of new resource discovery.
- `global_replicator_need`: Based on the current population relative to the `environment.carrying_capacity` and the overall swarm health.

### 3.3. Gender, Reproduction, and Wisdom

To introduce deeper social dynamics and a more realistic population model, agents will have an immutable `gender`, assigned at birth. This is not merely a biological flag, but a driver of behavior and cognitive diversity (the "wisdom thing").

**Gender Model:**
```rust
pub enum Gender {
    Male,
    Female,
    Asexual, // Represents the original parthenogenesis model
}
```

**Reproduction Model:**
- **Asexual:** Can replicate alone (parthenogenesis), as per the current `Intent::Replicate`. This might be common for foundational roles like `Builder`.
- **Sexual:** Requires two agents of compatible genders (`Male` and `Female`) to be in proximity and both signal intent to replicate. This creates a new social coordination challenge. The `World` will need a "mating" resolution phase. The resulting child will inherit a mix of traits from both parents.

**The "Wisdom" Aspect (Cognitive Diversity):**
Gender will influence the probability distribution of `Archetype` assignment at birth. This creates innate, population-level cognitive biases.

| Gender | Common Archetypes | Behavioral Tendency |
|---|---|---|
| **Male** | `Contrarian`, `Explorer`, `Opportunist` | Higher risk tolerance, exploration, individualistic reward-seeking. |
| **Female** | `Generalist`, `Historian`, `Purist` | Higher focus on social cohesion, long-term stability, and knowledge preservation. |
| **Asexual**| `Builder`, `Purist` | Task-focused, less engaged in complex social dynamics. |

This creates a fundamental tension: the swarm must not only manage its population size but also its gender ratio to maintain a healthy balance of cognitive strategies.

### 3.4. Culture and Memetic Evolution

To achieve true societal learning, the swarm must be able to transmit successful behaviors and ideas non-genetically. This is the role of culture. We will introduce the concept of **Memes**: discrete, replicable units of cultural information.

**Meme Model:**
A `Meme` is a pattern of behavior or a piece of abstract knowledge that can be observed, copied, and spread.

```rust
// Conceptual addition to core.rs
pub enum Meme {
    // A specific, successful foraging path or technique
    ForagingPattern { id: String, path_hash: u64, avg_reward: f32 },
    // A successful building pattern or location choice
    BuildingTechnique { id: String, location_hash: u64, structure_type: String },
    // A widely accepted CONTEXT claim that has become a "social norm" or "scientific law"
    SocialNorm { context_claim_id: String },
    // A set of rules for a competitive or cooperative interaction with a defined goal
    Game { id: String, rules_hash: u64, complexity: f32 },
}
```

**Meme Transmission:**
Agents (especially `Observer` and `Child` roles) will have a new `ObserveAndLearn` intent. When observing a highly successful agent (high λ or high recent reward), they have a chance to copy a `Meme` from that agent's "repertoire."

**Impact on Decision-Making:**
An agent's decisions will now be influenced by a third factor, alongside its innate Archetype and the global Swarm Priorities: its learned **Culture**. An agent that has learned a successful `ForagingPattern` meme will be more likely to follow that pattern, even if it slightly contradicts its immediate perceptions. This is how traditions and "best practices" form.

### 3.5. Agent Memory: The Chronicle

To enable learning and reflection, each agent will maintain a `chronicle`: a fixed-size, append-only log of significant personal events.

```rust
// Conceptual addition to agent.rs

pub struct Agent {
    // ... existing fields
    pub chronicle: Vec<AgentEvent>,
}

pub enum AgentEvent {
    RoleChange { from: Role, to: Role, tick: u32 },
    HighReward { action: Intent, reward: f32, tick: u32 },
    LowReward { action: Intent, reward: f32, tick: u32 },
    ClaimCountered { claim_id: String, tick: u32 },
}
```

### 3.6. Implementation in `agent.rs`

The `decide()` method's role-switching logic will be refactored into a `match self.archetype { ... }` block.

```rust
// Conceptual change in agent.rs

if self.role_cooldown == 0 && rng.gen_bool(0.1) {
    let new_role = match self.archetype {
        Archetype::Generalist => {
            // Current logic: find the most needed role based on swarm ratios.
            // NEW: Prioritize roles based on global Swarm Task Priorities.
            find_role_based_on_global_priorities(&percepts)
        },
        Archetype::Purist => {
            // New logic: find the role that best matches self.traits.
            find_best_role_for_traits(&self.traits)
        },
        Archetype::Contrarian => {
            // New logic: find the least common role in percepts.
            find_least_common_role(&percepts)
        },
        Archetype::Opportunist => {
            // Future logic: find role with highest historical reward.
            find_most_profitable_role(&self.history)
        },
        Archetype::Historian => {
            // New logic: analyze chronicle and claims, potentially deposit a CONTEXT claim.
            analyze_history_and_generate_theory(&self.chronicle, &percepts)
        },
        Archetype::Gamewright => {
            // New logic: observe interactions and attempt to formalize a new Game Meme.
            invent_game_from_patterns(&percepts)
        }
    };

    if let Some(role) = new_role {
        if role != self.role {
            return Intent::AdoptRole(role);
        }
    }
}
```

---

## 4. Roadmap

This framework can be implemented incrementally.

### Phase 1: Implement Purist vs. Generalist (Completed)
- **Task:** ~~Replace `is_specialist` with `archetype: Archetype`.~~ (Done)
- **Task:** ~~Implement the `Generalist` (global needs) and `Purist` (trait-based) decision paths in `agent.rs`.~~ (Done)
- **Goal:** Validate that this split preserves role diversity more robustly than the simple probability reduction. (Validated)

### Phase 2: Implement Contrarian & Opportunist Archetypes
- **Task:** Add the `Contrarian` archetype and its "inverse needs" logic.
- **Task:** Add a simple `recent_reward` field to `Agent` and implement the `Opportunist` logic.
- **Goal:** Test the swarm's resilience against monoculture and observe if simple learning leads to more effective individual specialization.

### Phase 3: Implement Gender & Mating
- **Task:** Add the `gender: Gender` enum and field to `agent.rs`.
- **Task:** Update the `World`'s replication logic to handle both asexual and sexual reproduction, requiring agent pairing.
- **Goal:** Create a more realistic population model and introduce a new layer of social coordination challenge.

### Phase 4: Implement Messengers
- **Task:** Add the `Messenger` archetype.
- **Task:** Implement logic for agents to identify information-sparse zones, "collect" claim data, and re-broadcast it in dense zones.
- **Goal:** Prevent the loss of valuable, peripheral claims and improve the swarm's overall map knowledge.

### Phase 5: Implement Memory and Historians
- **Task:** Add the `chronicle` (event log) to the `Agent` struct.
- **Task:** Implement the `Historian` archetype and its logic for analyzing history and generating `CONTEXT` claims.
- **Goal:** Enable the swarm to perform meta-analysis on its own behavior, creating a foundation for true collective learning.

### Phase 6: Implement Culture and Memetics
- **Task:** Define the `Meme` enum and add a `repertoire: Vec<Meme>` to the `Agent` struct.
- **Task:** Implement the `ObserveAndLearn` intent, allowing agents to copy memes from successful peers.
- **Task:** Modify the `decide()` logic to allow an agent's learned memes to influence its actions.
- **Goal:** Allow for the non-genetic transmission of successful strategies, creating a true cultural evolution that operates on top of the genetic and social layers.

### Phase 7: Emergent Recreation and Game Theory
- **Task:** Add the `Gamewright` archetype and the `Game` meme.
- **Task:** Implement an `InventGame` intent for Gamewrights and a `PlayGame` intent for other agents.
- **Task:** Link game performance (winning/losing) to minor, non-critical reputation (λ) adjustments.
- **Goal:** Create a sandbox for observing the emergence of abstract strategy, social recreation, and non-survival-based value systems.

---

## 5. Expected Outcomes

- **Increased Resilience:** A diverse cognitive portfolio makes the swarm less susceptible to single points of failure in its strategy.
- **Stable Specialization:** Key roles (Observer, Attester) will be preserved by Purists, even when not immediately "needed" by the majority.
- **Faster Adaptation:** Contrarians and Opportunists will explore new strategies more readily than the reactive Generalists.
- **Emergent Intelligence:** Historians will allow the swarm to generate and test its own theories, moving beyond simple reaction to active, collective cognition.
- **Cultural Evolution:** The swarm will develop and transmit "traditions"—proven strategies that allow it to solve problems more efficiently over time, creating a persistent, evolving civilization.
- **Abstract Thought:** The invention and playing of games will demonstrate a new level of abstract reasoning, where agents can create and pursue arbitrary goals within a shared ruleset, purely for social or intellectual reward.

This framework elevates the simulation from a study of homogeneous agents to a richer, more realistic model of a society composed of different "personalities." It is the natural next step in exploring the dynamics of complex adaptive systems.
