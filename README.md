# QueryBuilder LLM

An intelligent query builder that converts natural language to SQL and MongoDB queries using LLMs, executes them, and interprets the results.

## Features

- Convert natural language to SQL (PostgreSQL) and MongoDB queries using LLMs (currently using Ollama via `langchain-ollama`)
- Dynamic schema introspection for both PostgreSQL and MongoDB
- Execute generated queries against your configured database
- Automatically interpret query results in natural language using an LLM
- Support for both SQL and NoSQL databases
- Offline LLM support via Ollama (requires Ollama to be running with specified model)
- Customizable prompt templates for query generation and interpretation
- Environment variable management using `python-decouple`

## Installation

1. Clone the repository:

```bash
git clone https://github.com/karanparekh11/query-builder-llm.git
cd query-builder-llm
```

2. Install dependencies:

Ensure you have Python 3.8+ and pip installed. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Set up Environment Variables:

Copy the example environment file and edit it with your database credentials and settings. The project uses `python-decouple` to load these variables.

```bash
cp .env.example .env
# Edit .env with your database credentials and settings
```

### Environment Variables

The following environment variables are required in your `.env` file:

- **PostgreSQL Connection:**

  - `POSTGRES_HOST`: PostgreSQL host address
  - `POSTGRES_PORT`: PostgreSQL port number
  - `POSTGRES_DATABASE`: PostgreSQL database name
  - `POSTGRES_USERNAME`: PostgreSQL username
  - `POSTGRES_PASSWORD`: PostgreSQL password

- **MongoDB Connection:**

  - `MONGODB_CONNECTION_STRING`: MongoDB connection string (e.g., `mongodb://user:password@host:port/dbname`). Ensure the database name is included in the connection string.

- **LLM Configuration:**

  - `LLM_MODEL`: Name of the Ollama model to use (e.g., `llama2`, `mistral-openorca`). **Default: `llama2`**.
  - `LLM_BASE_URL`: URL of the Ollama API (e.g., `http://localhost:11434`). **Default: `http://localhost:11434`**.

- **Application Settings:**
  - `DEBUG`: Set to `True` for debugging. **Default: `False`**.
  - `LOG_LEVEL`: Logging level (e.g., `INFO`, `DEBUG`, `ERROR`). **Default: `INFO`**.

Example `.env` file:

```env
# Database Connection Strings
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=your_postgres_db
POSTGRES_USERNAME=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password

MONGODB_CONNECTION_STRING=mongodb://your_mongo_user:your_mongo_password@localhost:27017/your_mongo_db

# LLM Configuration
LLM_MODEL=llama2
LLM_BASE_URL=http://localhost:11434

# Application Settings
DEBUG=False
LOG_LEVEL=INFO
```

4. Run Ollama:

Ensure you have [Ollama](https://ollama.ai/) installed and running with the LLM model specified in your `.env` file (e.g., `llama2`). You can pull models using the command `ollama pull <model_name>`.

## Usage

The project provides an interactive command-line interface.

Run the main script:

```bash
python main.py
```

The script will now use the database type configured in your `.env` file. Enter your natural language query when prompted. After processing, it will display the generated query and a natural language interpretation of the results.

## Supported LLMs

Currently integrated with Ollama, supporting any model compatible with `langchain-ollama`. Recommended models include `llama2`, `mistral-openorca`, and `codellama`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License
