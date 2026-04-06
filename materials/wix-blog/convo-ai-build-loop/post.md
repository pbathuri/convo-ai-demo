# Convo AI was fun until progression logic got real

Convo AI looked great in the first demo. People saw points, streaks, and challenge cards and said, "this is engaging." Then I dug into progression behavior and realized half the challenge was not UI. It was consistency.

## What I built

I built a gamified learning prototype with task progression, milestone gating logic, and state transitions that needed to stay stable across repeated sessions.

## Why I built it

I wanted to test whether learning workflows can feel game-like without becoming shallow reward loops.

## The build

- Streamlit-centered interface for fast iteration
- structured task map and progression checkpoints
- state handling for streak and milestone conditions

## What broke and what I learned

My early logic let users hit milestones through odd edge paths. That made rewards feel random. I learned to value boring state rules and explicit checks before adding another visible feature.

## Current status and next step

Current status is a solid prototype narrative with a clearer architecture direction. Next step is collecting visual artifacts and tightening challenge library quality.

Links:
- GitHub profile: https://github.com/pradyotbathuri
- Portfolio case: `portfolio/convo-ai-gamified-learning.md`
