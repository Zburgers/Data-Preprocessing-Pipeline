# Database Structure

## PostgreSQL Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Datasets Table

```sql
CREATE TABLE datasets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    source_type VARCHAR(50) NOT NULL, -- 'upload', 'api', 'scheduled'
    modality VARCHAR(50) NOT NULL, -- 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'
    file_path VARCHAR(255), -- S3/MinIO path
    file_size BIGINT,
    file_type VARCHAR(50),
    row_count INTEGER,
    column_count INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);
```

### ML Tasks Table

```sql
CREATE TABLE ml_tasks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    modality VARCHAR(50) NOT NULL, -- 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'
    task_type VARCHAR(50) NOT NULL, -- 'classification', 'regression', 'ner', 'object_detection', etc.
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Pipeline Steps Table

```sql
CREATE TABLE pipeline_steps (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    step_type VARCHAR(50) NOT NULL, -- 'transform', 'filter', 'augment', etc.
    modality VARCHAR(50) NOT NULL, -- 'text', 'tabular', 'image', 'audio', 'video', 'multimodal'
    class_name VARCHAR(100) NOT NULL, -- The actual class implementing this step
    parameters JSONB, -- Default parameters
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Pipelines Table

```sql
CREATE TABLE pipelines (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    ml_task_id INTEGER REFERENCES ml_tasks(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    is_template BOOLEAN DEFAULT FALSE,
    configuration JSONB
);
```

### Pipeline Configurations Table

```sql
CREATE TABLE pipeline_configurations (
    id SERIAL PRIMARY KEY,
    pipeline_id INTEGER REFERENCES pipelines(id) ON DELETE CASCADE,
    step_id INTEGER REFERENCES pipeline_steps(id) ON DELETE CASCADE,
    order_index INTEGER NOT NULL,
    parameters JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Jobs Table

```sql
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    dataset_id INTEGER REFERENCES datasets(id) ON DELETE CASCADE,
    pipeline_id INTEGER REFERENCES pipelines(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL, -- 'pending', 'processing', 'completed', 'failed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    result_path VARCHAR(255), -- S3/MinIO path to the processed dataset
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    job_metadata JSONB
);
```

### Exports Table

```sql
CREATE TABLE exports (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    export_type VARCHAR(50) NOT NULL, -- 'huggingface', 'pytorch', 'tensorflow', 'csv', 'json'
    file_path VARCHAR(255), -- S3/MinIO path
    file_size BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);
```

## Redis Structure

### Job Queues

- `default`: Default queue for general tasks
- `upload`: Queue for file upload processing
- `text`: Queue for text data processing
- `tabular`: Queue for tabular data processing
- `image`: Queue for image data processing
- `audio`: Queue for audio data processing
- `video`: Queue for video data processing

### Caching

- Dataset metadata cache
- Pipeline configuration cache
- User session cache
- API rate limiting

## S3/MinIO Structure

```
/raw/
    /{user_id}/
        /{dataset_id}/
            data.csv
            metadata.json

/processed/
    /{user_id}/
        /{job_id}/
            data/
            metadata.json
            config.json

/exports/
    /{user_id}/
        /{export_id}/
            data/
            metadata.json
``` 