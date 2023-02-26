# algove

Algove (**Algo**rithim  Alc**ove**) is a fast and light-weight framework for building
algorithms. It is meant to simplify and bake-in some of the best practices I have 
seen and remove some of the footguns common to machine learning workflows.

[Read the full Documentation](https://ecurtin2.github.io/algove/)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=606537234)


## Goals

- Provide interactively fast experience like you would get inside a notebook, without one
- Reduce footguns
    - the full lifecycle is documented, reproducible and tracked as much as possible
    - make it easy to avoid poorly specified data formats (pickle, csv, etc)
- Support scaling to medium-data where possible
- Dramatically Reduce effort and/or need for documentation of ML/algorithmic development
- Support testing of pipelines


## Non-goals

- Brevity (we believe explicit is better than implicit)
- AutoML
- distributed compute (but flexible enough to work with spark/dask if others want to implement)

## Develop/Test locall in VSCode

```
git clone https://github.com/ecurtin2/algove:dev
cd algove
docker compose pull
code .
```
Then click "Reopen in Devcontainer" when prompted.