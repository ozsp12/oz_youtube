# Data documentation

## Source data

`streaming_platform/estimativa_dou_2021.csv` is a semicolon-delimited table containing 5,570 Brazilian municipalities and the fields `uf`, `cidade`, and `populacao_estimada`. The values correspond to the 2021 IBGE municipal population estimates published in the *Diário Oficial da União*. The aggregate total in the included file is 213,317,639.

Official context: https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/31461-ibge-divulga-estimativa-da-populacao-dos-municipios-para-2021

`streaming_platform/uf_populacao_br_2021.csv` is a legacy derived copy with state names and a serialized index column. It is retained to preserve the original project history but is not consumed by the refactored generator.

## Generated tables

### `state_population`

| Field | Meaning |
|---|---|
| `uf` | Federative-unit code |
| `state_name` | Federative-unit name |
| `population` | Sum of municipal estimates |
| `sampling_probability` | State population divided by the national total |

### `catalog`

| Field | Meaning |
|---|---|
| `artist_id` | Deterministic synthetic artist identifier |
| `album_id` | Deterministic synthetic album identifier |
| `track_id` | Deterministic synthetic track identifier |
| `sampling_probability` | Dirichlet-drawn track weight |

### `users`

| Field | Meaning |
|---|---|
| `user_id` | Deterministic synthetic identifier |
| `age_years` | Scenario draw from a bounded normal distribution |
| `sex_state` | Scenario category sampled from configured probabilities |
| `uf` | State sampled from public aggregate population weights |

### `events`

| Field | Meaning |
|---|---|
| `event_id` | Deterministic synthetic event identifier |
| `event_timestamp` | Regular simulation tick |
| `user_id` | Foreign key to `users` |
| `track_id` | Foreign key to `catalog` |
| `listening_seconds` | Scenario draw between 30 and 300 seconds |

## Governance statement

The generated rows are simulation outputs and contain no original individual-level observations. This reduces the disclosure concern for this specific project but does not justify a general claim that synthetic data are anonymous. Generators trained on confidential microdata require explicit privacy attacks, membership-inference evaluation, attribute-inference evaluation, and a documented utility–risk analysis before release.
