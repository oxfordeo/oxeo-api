<img src="oxeo_logo.png" alt="oxeo logo" width="600"/>

[OxEO](https://www.oxfordeo.com/) is an earth observation water risk company. This repository builds and deploys OxEO's data pipeline Flows via Prefect. OxEO's data service is comprised of three repos: [oxeo-flows](https://github.com/oxfordeo/oxeo-flows), [oxeo-water](https://github.com/oxfordeo/oxeo-water), and [oxeo-api](https://github.com/oxfordeo/oxeo-api). This work was generously supported by the [European Space Agency Φ-lab](https://philab.esa.int/) and [World Food Programme (WFP) Innovation Accelerator](https://innovation.wfp.org/) as part of the [EO & AI for SDGs Innovation Initiative](https://wfpinnovation.medium.com/how-can-earth-observation-and-artificial-intelligence-help-people-in-need-5e56efc5c061).

Copyright © 2022 Oxford Earth Observation Ltd.

---

# oxeo-api
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This repo provides the API and database version control for the oxeo-api data service. This repo is intended to be deployed via an [AWS Lambda](https://aws.amazon.com/lambda/) service. Routes are built with [FastAPI](https://fastapi.tiangolo.com/). The production endpoint is https://api.oxfordeo.com.


## Installation
```
pip install .
```

## DB Management

### Initial Setup

Connect to the db:

    psql -h hostname -p portNumber -U userName dbName -W

Install extensions:

    CREATE EXTENSION postgis;
    CREATE EXTENSION hstore;


### Revisions

With [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html#the-migration-environment):

Auto-Generate a revision:

    alembic revision --autogenerate -m "<my revision commit message>"

Update the db:

    alembic upgrade head

You may need to tidy up the migration script at `./alembic/versions/<hash>_<my_commit_message>.py`


## Development
```
pip install -e .[dev]
pre-commit install
```

Run tests:
```
tox
```

## Deployment

Deployment to AWS Lambda uses [Github Actions](.github/workflows/) for Continuous Integration and Deployment. Pushes to `main` are automatically built and deployed.
