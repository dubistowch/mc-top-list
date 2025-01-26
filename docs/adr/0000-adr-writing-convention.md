# ADR 0000: ADR Writing Convention

## Status
Accepted

## Context
To ensure consistency and clarity in documenting architecture decisions for the Minecraft 插件模組爬蟲 project, we need a standardized approach to writing and organizing Architecture Decision Records (ADRs). A convention provides a structured way for team members to capture and share decisions, making it easier to maintain the project's design history over time.

## Decision
We will follow the below ADR Writing Convention:

### Naming & Location
- **Filename Convention**: `NNNN-title-with-dashes.md`, where `NNNN` is a sequential, zero-padded number (e.g., `0001-initialize-project.md`).
- **Directory**: ADRs will be stored in a dedicated folder: `docs/adr/`.

### ADR Document Structure
Each ADR file should include the following sections:

1. **Title and Identifier**
   - The first line of the file is `# ADR NNNN: Short Title` (matching the filename).

2. **Status**
   - **Proposed**: The team is still discussing this decision; not yet finalized.
   - **Accepted**: The decision has been agreed upon and is in effect.
   - **Rejected**: The decision was proposed but not adopted.
   - **Superseded**: A later ADR replaces or reverses this decision.

3. **Context**
   - Summarize the background, the problem being solved, and reasons for the decision.
   - Include any relevant business or technical constraints.

4. **Decision**
   - Clearly state the decision in a concise manner.
   - Example: "We will implement the scraper in Python 3.9." 

5. **Consequences**
   - List the outcomes, both positive and negative.
   - Describe the impact on maintenance, complexity, cost, and other dimensions.
   - Include potential future changes if the decision no longer meets requirements.

6. **Related ADRs**
   - List any related ADRs that this decision affects or is affected by.
   - Use the format: `- [ADR NNNN](./NNNN-title-with-dashes.md)`

7. **Date**
   - Include the date when the ADR was created or last modified.
   - Use the format: `Month DD, YYYY`

### Referencing Other ADRs
- If a new ADR modifies or replaces a previous one, link to the old ADR.
- Example: "This ADR supersedes [ADR 0005](./0005-old-decision.md)."

### Tone & Style
- **Concise**: Keep the ADR to one or two pages maximum.
- **Clear**: Explain terms or acronyms unfamiliar to new team members.
- **Action-Oriented**: Focus on the decision being made and its rationale.

### Lifecycle of an ADR
- **Proposal**: Team members discuss the draft ADR until reaching consensus.
- **Acceptance**: Merge the ADR into the main branch and mark **Status** as `Accepted`.
- **Revisiting**: Write a new ADR to modify or supersede an old one. Do not rewrite history.

## Consequences
- **Pros**:
  - Ensures all design decisions are captured clearly.
  - Simplifies onboarding for new contributors.
  - Allows for iterative decision-making with historical context.
- **Cons**:
  - Requires discipline and regular updates to maintain.
