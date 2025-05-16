import datetime
from typing import Dict, Any, List
from .schema_introspector import SchemaIntrospector
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
import json
from typing import List, Dict, Any
from bson import ObjectId  # ✅ Make sure you have `pymongo` or `bson` installed
from datetime import datetime


class MongoDBQueryBuilder:
    """
    Builds and executes MongoDB aggregation pipelines via an LLM.
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
        self.llm = OllamaLLM(
            model=llm_model, temperature=temperature, num_ctx=num_ctx, format="json"
        )
        self.target = None
        self.query_prompt = PromptTemplate(
            input_variables=["schema", "query"],
            template=(
                """
                You are a MongoDB expert familiar with aggregation pipelines.
                Given this collection schema:
                {schema}
                Convert the natural‑language request:
                {query}
                into a MongoDB aggregation pipeline.
                Return **only** the array of stages object itself, formatted exactly like this example (no wrapping object, no extra keys, no markdown, no explanation):
                Example:
                {{ pipeline:[
                {{ "$group": {{ "_id": null, "count": {{ "$sum": 1 }} }} }},
                {{ "$match": {{ "status": {{ "$exists": true }} }} }},
                {{ "$count": "totalDocuments" }}
                ] }}
                Do not include any other fields or commentary.
                Create Respected pipelines for query.
                """
            ),
        )

    def generate_query(self, nl_query: str, **kwargs) -> str:
        schema = self.introspector.get_schema_info(nl_query, **kwargs)
        formatted = self._format(schema)
        raw = self.llm.invoke(
            self.query_prompt.format(schema=formatted, query=nl_query)
        )
        return self._clean(raw)

    def execute_query(self, pipeline_str: str) -> List[Dict[str, Any]]:
        pipeline = self._parse_pipeline(pipeline_str)
        print(f"Parsed pipeline: {pipeline}")
        db = self.introspector.client[self.introspector.get_database_name()]
        if not self.introspector.target:
            self.introspector.target = list(self.introspector.get_schema_info().keys())[
                0
            ]
        print(f"Executing pipeline on collection: {self.introspector.target}")
        return list(db[self.introspector.target].aggregate(pipeline))

    @staticmethod
    def safe_json(obj: Any):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    def interpret_results(self, docs: List[Dict[str, Any]], nl_query: str) -> str:
        prompt = PromptTemplate(
            input_variables=["query", "results"],
            template=(
                "Analyse the following results for the query: '{query}'\n\n"
                "{results}\n\nProvide a concise and accurate summary."
            ),
        )

        try:
            serialized_results = json.dumps(
                docs, indent=2, default=MongoDBQueryBuilder.safe_json
            )
        except Exception as e:
            raise ValueError(f"Failed to serialize documents: {e}")

        return self.llm.invoke(
            prompt.format(query=nl_query, results=serialized_results)
        ).strip()

    def _format(self, schema: Dict[str, Any]) -> str:
        lines = []
        for name, info in schema.items():
            lines.append(f"Collection {name}:")
            for f in info.get("fields", []):
                lines.append(f"  - {f['name']}: {f['type']}")
            for idx in info.get("indexes", []):
                lines.append(f"  idx: {idx}")
        return "\n".join(lines)

    def _parse_pipeline(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse a JSON string into a MongoDB aggregation pipeline:
        - If it's an object with a 'pipeline' key, unwrap it.
        - If it's a single stage object, wrap it in a list.
        - Otherwise ensure it's a list of dicts.
        """
        # Parse JSON
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as e:
            # Propagate JSON errors
            raise ValueError(f"Invalid JSON: {e}") from e

        # Unwrap {"pipeline": [...]} if present
        if isinstance(payload, dict) and "pipeline" in payload:
            pipeline = payload["pipeline"]
        else:
            pipeline = payload

        # If it's a single stage, wrap it
        if isinstance(pipeline, dict):
            pipeline = [pipeline]

        # Validate final structure
        if not isinstance(pipeline, list) or not all(
            isinstance(stage, dict) for stage in pipeline
        ):
            raise ValueError(
                f"Invalid pipeline format: {text!r}. Expected a JSON array of objects or an object with a 'pipeline' key."
            )

        return pipeline

    def _clean(self, text: str) -> str:
        return text.strip().lstrip("```json").rstrip("```")
