# Changelog

## [4.0.1] - 2026-05-03

Refactored the project as an installable Python package with Airflow 3.

### Added
- Added `pyproject.toml` for packaging ETL modules.
- Added unit tests for all ETL modules.
- Added `CHANGELOG.md` to track project history.

### Changed
- Restructured `src/` into `ctn_monitor/etl/` package.
- Replaced standalone `Dockerfile` with an Airflow 3 Docker Compose setup.
- Simplified Makefile targets for Docker Compose.
- Bumped dependency versions.

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
- Removed redundant reading of the `.env` file.
- Updated backlog URL.
- Updated the services used in the architecture diagram.

## [2.0.2] - 2024-08-02

Enhanced pipeline execution.

### Added
- Added product backlog for review.
- Calculated operational costs in the production scenario.
- Added directory setup for the pipeline.
- Added Makefile for recompilation.

### Changed
- Updated Dockerfile to reduce image size.
- Improved README instructions.

## [2.0.1] - 2024-07-22

Revamped the data pipeline and dashboard design.

### Changed
- Enhanced the dashboard design for a more professional appearance.
- Refactored the data pipeline into distinct modules.
- Switched PDF table extraction from Tabula-py to the Adobe PDF Extract API.

## [1.0.1] - 2022-08-25

Initial repository.
