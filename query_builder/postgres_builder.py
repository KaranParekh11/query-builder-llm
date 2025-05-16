from typing import Dict, Any
from .schema_introspector import SchemaIntrospector
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import pandas as pd
from sqlalchemy import text


class PostgresQueryBuilder:
    """
    Builds and executes SQL queries via an LLM.
    """

    def __init__(
        self,
        introspector: SchemaIntrospector,
        llm_model: str,
        temperature: float = 0.1,
        num_ctx: int = 4096,
    ):
        if not llm_model:
            raise ValueError("`llm_model` is required")

        self.introspector = introspector
        self.llm = OllamaLLM(model=llm_model, temperature=temperature, num_ctx=num_ctx)
        self.query_prompt = PromptTemplate(
            input_variables=["schema", "query"],
            template=(
                "You are a PostgreSQL expert.\n\n"
                "Given the table schema:\n{schema}\n\n"
                "Convert the following natural language request into a valid and optimized RAW SQL query:\n\n"
                "'{query}'\n\n"
                "Format the query so that:\n"
                '- Table names are always wrapped in double quotes (e.g., "user")\n'
                "- Column names should not be quoted unless absolutely necessary\n"
                "- Do not include comments, explanations, or extra text\n"
                "- Only return the SQL statement, ready to use with SQLAlchemy's text() function"
            ),
        )

    def generate_query(self, nl_query: str, **kwargs) -> str:
        schema = self.introspector.get_schema_info(nl_query, **kwargs)
        formatted = self._format(schema)
        raw = self.llm.invoke(
            self.query_prompt.format(schema=formatted, query=nl_query)
        )
        return raw

    def execute_query(self, sql: str) -> pd.DataFrame:
        try:
            with self.introspector.engine.connect() as conn:
                result = conn.exec_driver_sql(sql)
                return result.fetchall()

        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")

    def interpret_results(self, results, nl_query: str) -> str:
        prompt = PromptTemplate(
            input_variables=["query", "results"],
            template=(
                "Analyse '{query}' results:\n{results}\n" "Provide a concise summary."
            ),
        )
        return self.llm.invoke(prompt.format(query=nl_query, results=results)).strip()

    def _format(self, schema: Dict[str, Any]) -> str:
        lines = []
        for table, info in schema.items():
            lines.append(f"Table {table}:")
            for c in info.get("columns", []):
                lines.append(f"  - {c['name']}: {c['type']}")
            for r in info.get("relationships", []):
                lines.append(f"  rel: {r}")
        return "\n".join(lines)

    def _clean(self, text: str) -> str:
        return text.strip().lstrip("```sql").rstrip("```")
