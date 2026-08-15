# Synthetic Data

This repository provides reproducible, simulation-based generators for educational datasets. The current project models a hypothetical music-streaming platform with normalized catalog, user, and event tables.

Synthetic data are useful for software testing, demonstrations, controlled experiments, and methodological research. They are not automatically representative, fair, private, or anonymous. Those properties require separate empirical evaluation. A table can look convincing and still be statistically useless—the usual triumph of cosmetics over measurement.

## Current project

The streaming-platform generator combines explicit scenario parameters with public aggregate population weights. It does not learn from individual customer records.

| Component | Description |
|---|---|
| [`src/synthetic_data/streaming.py`](src/synthetic_data/streaming.py) | Documented `StreamingPlatformGenerator` implementation |
| [`streaming_music_data.ipynb`](streaming_platform/streaming_music_data.ipynb) | Academic notebook with assumptions, results, and quality checks |
| [`estimativa_dou_2021.csv`](streaming_platform/estimativa_dou_2021.csv) | IBGE municipal population estimates used as aggregate weights |
| [`uf_populacao_br_2021.csv`](streaming_platform/uf_populacao_br_2021.csv) | Legacy derived snapshot retained for provenance; not used by the new generator |
| [`DATA.md`](DATA.md) | Input and generated-table documentation |
| [`REFERENCES.md`](REFERENCES.md) | Bibliography on synthetic data, utility, and disclosure risk |
| [`requirements.yml`](requirements.yml) | Reproducible Conda environment |
| [`tests/`](tests/) | Unit, integrity, reproducibility, and notebook tests |

## Installation

```bash
conda env create -f requirements.yml
conda activate synthetic-data
python -m pip install -e .
jupyter lab streaming_platform/streaming_music_data.ipynb
```

Start JupyterLab from the repository root. The notebook uses root-relative project paths.

## Python usage

```python
from synthetic_data import StreamingConfig, StreamingPlatformGenerator

config = StreamingConfig(seed=42, n_users=1_000)
generator = StreamingPlatformGenerator(config)
tables = generator.generate("streaming_platform/estimativa_dou_2021.csv")

catalog = tables["catalog"]
users = tables["users"]
events = tables["events"]
print(generator.quality_report(tables))
```

The default scenario produces 360 tracks, 1,000 users, and 2,992 events. Recreating the generator with the same configuration reproduces all four tables exactly.

## Validation

```bash
python -m unittest discover -s tests -v
```

The suite checks configuration constraints, deterministic generation, source-data parsing, primary keys, foreign keys, expected table sizes, notebook structure, and Python syntax.

## Methodological boundaries

- State weights reflect aggregate 2021 population shares, not platform adoption.
- Age and sex-state distributions are scenario parameters rather than demographic estimates.
- No arbitrary state-specific preference or behavior coefficient is imposed.
- The generator does not establish similarity to any real streaming platform.
- Synthetic output derived from confidential microdata would still require disclosure-risk assessment; simulation alone is not a privacy guarantee.

## Author

**Dr. Osvaldo L. Santos-Pereira** — [Academic webpage](https://ozsp12.github.io/) · [Lattes](http://lattes.cnpq.br/6730251976463283) · [ORCID](https://orcid.org/0000-0003-2231-517X) · [Google Scholar](https://scholar.google.com/citations?user=HIZp0X8AAAAJ&hl=en) · [ResearchGate](https://www.researchgate.net/profile/Osvaldo-Santos-Pereira) · [GitHub](https://github.com/ozsp12) · [LinkedIn](https://www.linkedin.com/in/ozsp12) · [Substack](https://substack.com/@olsp1982) · [Medium](https://medium.com/@ozsp12) · [YouTube](https://www.youtube.com/@ozlsp12) · [X](https://x.com/ozsp12)

## Citation and reuse

Use [`CITATION.cff`](CITATION.cff) to cite this repository. No repository-wide license has been declared; citation metadata does not grant redistribution rights.
