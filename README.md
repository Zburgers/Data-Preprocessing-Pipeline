# Data Preprocessing Pipeline Platform

A universal, production-ready, and scalable data preprocessing pipeline platform for AI/ML developers.

## Overview

This platform accepts any raw data (text, tabular, audio, image, video, PDFs) and automatically transforms it into clean, model-ready datasets for popular AI tasks such as classification, regression, object detection, or NER.

## Features

- **Universal Data Input**: Support for CSV, JSON, TXT, JPG, MP4, WAV, PDF, and more
- **Automatic Detection**: Auto-detects data modality and suggests appropriate ML tasks
- **Customizable Pipelines**: Modular pipeline architecture with configurable transformation steps
- **Multiple Export Formats**: Export to HuggingFace Datasets, PyTorch Dataset, TensorFlow Datasets, or flat CSV/JSON
- **Modern UI**: Next.js frontend with intuitive step-by-step workflow
- **Scalable Backend**: FastAPI with Celery for asynchronous processing
- **Enterprise Ready**: Dockerized, horizontally scalable, with comprehensive logging and security

## System Architecture

- **Frontend**: Next.js + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Celery + Redis
- **Storage**: PostgreSQL (metadata) + S3 (data)
- **Processing**: Modular pipeline engine with pluggable transformation steps

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 18+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/data-preprocessing-pipeline.git
cd data-preprocessing-pipeline

# Start the application using Docker Compose
docker-compose up -d
```

The application will be available at http://localhost:3000

## Documentation

Detailed documentation can be found in the `docs/` directory.

## License

MIT