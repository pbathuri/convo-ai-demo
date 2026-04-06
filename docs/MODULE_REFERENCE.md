# Module reference

Quick index of Python modules and their responsibilities. Paths are relative to the repository root.

## Entrypoint

| File | Responsibility |
|------|----------------|
| `app/app.py` | Streamlit app: sidebar, conversation loop, OpenAI calls, export, charts |

## UI components (`components/`)

| Module | Responsibility |
|--------|----------------|
| `skill_map.py` | Renders the Duolingo-style skill map from progression data |
| `ui_blocks.py` | Dashboard widgets: emotion radar, scores, feedback, history, progress |
| `domain_styles.py` | Per-domain/subdomain colors and tone labels for the main pane |

## Engines (`app/services/`)

| Module | Responsibility |
|--------|----------------|
| `persona_engine.py` | Builds persona-related prompt fragments when used |
| `feedback_engine.py` | `build_feedback_prompt` — short coach-style feedback from history |
| `scoring_engine.py` | `build_score_prompt` — numeric score prompt for favorability |
| `scenario_engine.py` | Loads named scenarios from `data/scenarios.json` |
| `gamification_engine.py` | XP from score, streak checks, optional milestones |
| `voice_engine.py` | `record_and_transcribe` — audio file → text via SpeechRecognition |
| `voice_player.py` | `speak` — text-to-speech for AI replies |
| `voice_personality_engine.py` | Voice profile selection hooks from emotion data |
| `voice_profile.py` | Additional voice profile helpers |
| `interruption_engine.py` | Suggests when the AI might “interrupt” based on message length |
| `personality_evolution.py` | `evaluate_user_tone` — short tone observation for context |
| `multi_agent_engine.py` | Panel definitions and `get_panel` for multi-agent simulations |
| `emotion_engine.py` | `evaluate_emotional_tone` — returns a **prompt** asking the model for JSON trait scores |
| `memory_engine.py` | `update_memory` / `get_memory_context` — structured session memory |
| `skill_tracker.py` | Rolling skill stats, lowest trait, time series for charts |
| `skill_tree.py` | Skill tree logic used with learning progression data |
| `reflection_engine.py` | `generate_reflection` — end-of-session reflection prompt text |
| `animation_registry.py` | CSS/emoji animation hints per subdomain |

### UI helpers (`app/services/ui/`)

| Module | Responsibility |
|--------|----------------|
| `subdomain_visuals.py` | Background gradients and persona labels per subdomain |

## Domain modules (`app/services/domains/`)

Each domain file follows a common pattern:

- **`get_subdomains()`** — Returns a list of selectable subdomain strings.
- **`generate_prompt(user_input, subdomain, goal, memory, traits)`** — Returns a prompt string or dict with a `prompt` key used as the system message for the assistant.

| Module | Topic |
|--------|--------|
| `political_conversation.py` | Political theory, ideologies, government, IR |
| `business_communication.py` | Professional communication scenarios |
| `philosophy.py` | Philosophical dialogue |
| `emotional_intelligence.py` | EQ-focused practice |
| `debate_simulation.py` | Debate-style exchanges |
| `satirical_political_commentary.py` | Satirical political voice |
| `ai_society.py` | AI ethics and society (includes extra helpers) |
| `sales_conversation.py` | Sales conversations |

## Tests and packaging

| File | Notes |
|------|--------|
| `setup.py` | Package metadata; entry point may need alignment with `app/app.py` |
| `test_plan.md` | Manual / planned test ideas at repo root |
