
The Six Lens Knowledge System

Overview

Every piece of knowledge in Explorer-d334 exists as a cube with six faces. Each face represents a different way of seeing the same truth.

```
        ⊡ CONTEXT (Green)
             ↑
    ◇ FICTION ← ◈ FACT → ◎ OPINION
    (Amber)   (Cyan)   (Purple)
             ↓
        ⊘ COUNTER (Red)
             ↓
        ? UNKNOWN (Grey)
```

The Six Lenses

◈ FACT (Cyan)

The prime verifiable statement. What is objectively true?

Keywords: "is", "are", "was", "evidence shows", "data indicates"

Example: "The Earth orbits the Sun once every 365.25 days"

⊘ COUNTER (Red)

The refutation or opposing argument. What challenges this?

Keywords: "however", "contrary", "disagree", "but", "actually"

Example: "Geocentric models placed Earth at the center of the universe"

◎ OPINION (Purple)

Personal or subjective perspective. What do I think?

Keywords: "I think", "I believe", "seems", "appears", "feels"

Example: "I think heliocentrism was a revolutionary idea"

◇ FICTION (Amber)

Speculative or narrative take. What if something else?

Keywords: "imagine", "what if", "could be", "perhaps", "story"

Example: "What if Earth's orbit slowly changed over millions of years?"

⊡ CONTEXT (Green)

Historical or wider framing. How did we get here?

Keywords: "history", "origin", "traditionally", "background", "research"

Example: "Copernicus first proposed heliocentrism in 1543"

? UNKNOWN (Grey)

What remains unresolved. What don't we know yet?

Keywords: "unknown", "mystery", "unresolved", "question", "unclear"

Example: "What other orbital mechanics remain undiscovered?"

Cube Integrity

Each cube has an integrity score based on:

· Completeness (40%) - How many of 6 faces are filled
· Quality (60%) - Average confidence of each entry

Score Grade Meaning
90-100 CRYSTALLINE Complete knowledge, high quality
65-89 COHERENT Complete knowledge, good quality
35-64 FORMING Partial knowledge, growing
0-34 SPARSE Just started, needs work

Active Knowledge Building

Explorer-d334 actively searches the web to fill missing lenses:

1. Identifies which lenses are missing from each cube
2. Searches the web for relevant content
3. Scores the source using Leighton Weight trust
4. Presents the proposal for your approval
5. Adds to the cube when approved
6. Learns from your feedback to improve future suggestions

Commands

```bash
# Add knowledge (auto-classified)
./forge remember "Your fact or perspective"

# View all cubes
./forge cubes

# View a specific cube
./forge cube <cube_id>

# Find missing lenses
./forge cube-scan

# Review pending web-sourced additions
./forge cube-pending

# Approve a suggested addition
./forge cube-approve <id> "Your feedback"

# Reject a suggestion
./forge cube-reject <id> "Reason for rejection"
```

Example: Building a Complete Cube

```bash
# Step 1: Start with a FACT
./forge remember "The Earth orbits the Sun"

# Step 2: Add COUNTER perspective
./forge remember "However, ancient geocentrists disagreed"

# Step 3: Add your OPINION
./forge remember "I think heliocentrism was revolutionary"

# Step 4: Add FICTION speculation
./forge remember "What if the orbit was elliptical?"

# Step 5: Add CONTEXT history
./forge remember "Copernicus proposed this in 1543"

# Step 6: Add UNKNOWN questions
./forge remember "What other solar system mysteries remain?"

# View your complete cube
./forge cubes
```

Visualization

The 3D Data Cube visualization (datacube_visualization.html) shows your cubes in 3D space, with:

· Cubes clustering by topic similarity
· Edges showing relationships between cubes
· Color-coded faces for each lens
· Zoom and rotation controls

---

Six perspectives. Complete knowledge. The forge sees all sides. 🔥
