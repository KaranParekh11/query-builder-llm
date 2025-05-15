# QueryBuilder LLM

An intelligent query builder that converts natural language to SQL and MongoDB queries using LLMs.

## Features

- Convert natural language to SQL (PostgreSQL) and MongoDB queries
- Execute generated queries against your database
- Automatically interpret query results in natural language
- Dynamic schema introspection
- Support for both SQL and NoSQL databases
- Offline LLM support via Ollama
- Customizable prompt templates
- Easy integration with existing projects

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/query-builder-llm.git
cd query-builder-llm
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

### Environment Variables

The following environment variables are required:

- `POSTGRES_CONNECTION_STRING`: PostgreSQL connection string
- `MONGODB_CONNECTION_STRING`: MongoDB connection string
- `LLM_MODEL`: LLM model to use (default: "mistral")
- `LLM_BASE_URL`: Ollama API URL (default: "http://localhost:11434")
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: "INFO")

Example `.env` file:

```env
POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/dbname
MONGODB_CONNECTION_STRING=mongodb://user:password@localhost:27017/dbname
LLM_MODEL=mistral
LLM_BASE_URL=http://localhost:11434
DEBUG=False
LOG_LEVEL=INFO
```

### Building Connection Strings

You can build PostgreSQL connection strings using the utility function:

```python
from query_builder.utils import build_postgres_connection_string

# Build a PostgreSQL connection string
conn_string = build_postgres_connection_string(
    host="localhost",
    port=5432,
    database="mydb",
    username="myuser",
    password="mypassword",
    ssl_mode="prefer"  # optional
)

# The resulting connection string will be:
# postgresql://myuser:mypassword@localhost:5432/mydb?sslmode=prefer
```

The function handles:

- URL encoding of special characters in the password
- Optional SSL mode configuration
- Proper formatting of the connection string

## Usage

### Basic Usage

```python
from query_builder import QueryBuilder
from query_builder.config import settings

# Initialize the query builder
qb = QueryBuilder(
    db_type="postgres",  # or "mongodb"
    connection_string=settings.get_connection_string("postgres")
)

# Generate query from natural language
query = qb.generate_query(
    "Show me all users from India who joined in 2024"
)

# Execute the query
results = qb.execute_query(query)

# Get natural language interpretation of results
interpretation = qb.interpret_results(results, "Show me all users from India who joined in 2024")
```

### Command Line Usage

```bash
# For PostgreSQL
python example.py --db-type postgres --query "Show me all users from India who joined in 2024"

# For MongoDB
python example.py --db-type mongodb --query "Show me all users from India who joined in 2024"
```

The script will:

1. Generate the appropriate database query
2. Execute the query against your database
3. Provide a natural language interpretation of the results

## Supported LLMs

- Mistral (via Ollama)
- GPT4All
- Other Ollama-compatible models

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
