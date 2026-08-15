# Análise de dados com DuckDB

Exercícios complementares de SQL analítico sobre eventos de consumo de vídeo, assinaturas e catálogo. O notebook combina `pandas` e DuckDB para explorar tabelas locais e formular consultas sem configurar um servidor de banco de dados.

## Arquivos

- [`analise.ipynb`](analise.ipynb): enunciados e consultas;
- [`events.csv`](events.csv): eventos observados;
- [`subscriptions.csv`](subscriptions.csv): assinaturas;
- [`videos.csv`](videos.csv): metadados dos vídeos.

Execute o notebook a partir desta pasta, pois os arquivos são carregados por caminhos relativos. Antes de interpretar as métricas, confira granularidade, chaves, unidades de tempo e possíveis duplicidades de cada tabela.
