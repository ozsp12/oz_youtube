# oz_youtube

Automated catalog of videos published on the [Osvaldo L. Santos-Pereira YouTube channel](https://www.youtube.com/@ozlsp12), with source code, notebooks, references, figures, and supplementary material.

The catalog is synchronized from YouTube metadata and regenerated automatically by GitHub Actions.

<!-- YOUTUBE-VIDEOS:START -->

## Videos

The catalog will be generated automatically by the synchronization workflow.

<!-- YOUTUBE-VIDEOS:END -->

## Repository structure

```text
src/       Python scripts for metadata extraction and README generation
data/      Generated metadata files
videos/    Supplementary material organized by YouTube video ID
.github/   GitHub Actions automation
```

## Manual execution

```bash
pip install -r requirements.txt
python src/extrair_videos_youtube.py --modo ytdlp --saida data/videos_canal_youtube.xlsx
python src/gerar_readme.py
```

The `yt-dlp` mode does not require an API key. The extractor also retains support for the official YouTube Data API v3.
