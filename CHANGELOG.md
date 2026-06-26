# Changelog

## [4.0.2] - 2026-06-26

Minor project configuration and pipeline execution updates.

### Added
- Added more comprehensive exclusions to `.gitignore` and `.dockerignore`.

### Changed
- Refactored imports in `ctn_monitor/__init__.py` and `ctn_monitor/etl/__init__.py`.
- Updated `airflow/dags/ctn_etl.py` to remove `end_date` and enable `catchup`.
- Updated grammatical tense in `README.md`.
- Formatted `RuntimeError` invocations in `ctn_monitor/etl/extract.py` and `ctn_monitor/etl/tabulate.py`.
- Cleared notebook metadata from Jupyter notebooks.
- Replaced `airflow/docker-compose.yaml` with `airflow/compose.yaml` and updated `makefile` targets `build` and `airflow`.
- Updated `pyproject.toml` with package name `ctn-monitor`, version `4.0.2`, and Python version requirement `~=3.12.0`.
- Replaced `imgs/solution_architect.png` with `imgs/diagram.drawio.png`.

### Removed
- Removed example sensitive values from `airflow/.env.example`.
- Removed all unit tests in the `tests/` directory.

## [4.0.1] - 2026-05-03

Refactored the project as an installable Python package with Airflow 3.

### Added
- Added `CHANGELOG.md` to track project history.
- Added `pyproject.toml` for packaging ETL modules.
- Added unit tests for all ETL modules.

### Changed
- Bumped dependency versions.
- Replaced standalone `Dockerfile` with an Airflow 3 Docker Compose setup.
- Restructured `src/` into `ctn_monitor/etl/` package.
- Simplified Makefile targets for Docker Compose.

### Removed
- Removed standalone `Dockerfile`, `main.py`, and `config/`.

## [3.0.1] - 2024-10-18

Minor improvement before archiving the repository.

### Changed
- Built Docker image with a multistage build to reduce image size.
- Compressed Docker image layers to reduce size.
- Specified the Python version in the Makefile.
- Updated README for consistency with other projects.

## [2.0.3] - 2024-08-23

Enhanced the pipeline folder structure.

### Changed
- Moved Dockerfile and main script to the root directory.
- Updated backlog URL.
- Updated the services used in the architecture diagram.

### Removed
- Removed redundant reading of the `.env` file.

## [2.0.2] - 2024-08-02

Enhanced pipeline execution.

### Added
- Added directory setup for the pipeline.
- Added Makefile for recompilation.
- Added product backlog for review.
- Calculated operational costs in the production scenario.

### Changed
- Improved README instructions.
- Updated Dockerfile to reduce image size.

## [2.0.1] - 2024-07-22

Revamped the data pipeline and dashboard design.

### Changed
- Enhanced the dashboard design for a more professional appearance.
- Refactored the data pipeline into distinct modules.
- Switched PDF table extraction from Tabula-py to the Adobe PDF Extract API.

## [1.0.1] - 2022-08-25

Initial repository.
