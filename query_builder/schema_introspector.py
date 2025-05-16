from typing import Dict, Any, Optional
from pymongo import MongoClient
from sqlalchemy import create_engine, MetaData, inspect
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM
import json


class SchemaIntrospector:
    """
    Introspects database schema for Postgres or MongoDB,
    and optionally selects the best table/collection via an LLM.
    """

    def __init__(
        self,
        db_type: str,
        connection_string: str,
        llm_model: Optional[str] = None,
        temperature: float = 0.1,
        num_ctx: int = 4096,
        schema_cache: Optional[Dict[str, Any]] = None,
    ):
        self.db_type = db_type.lower()
        self.connection_string = connection_string
        self.schema_cache = schema_cache
        self.target = None
        # Optional LLM for best-target selection
        if llm_model:
            self.llm = OllamaLLM(
                model=llm_model, temperature=temperature, num_ctx=num_ctx
            )
            self.selection_prompt = PromptTemplate(
                input_variables=["options", "query"],
                template=(
                    "You are a database expert. Given these options:\n\n"
                    "{options}\n\n"
                    "User goal: {query}\n\n"
                    "Which single option is best?  **Return exactly the name of collection**—no quotes, no parentheses, no explanations."
                ),
            )
        else:
            self.llm = None

        if self.db_type == "postgres":
            self._init_postgres()
        elif self.db_type == "mongodb":
            self._init_mongodb()
        else:
            raise ValueError(f"Unsupported db_type: {db_type}")

    def _init_postgres(self):
        self.engine = create_engine(self.connection_string)
        self.inspector = inspect(self.engine)

    def _init_mongodb(self):
        self.client = MongoClient(self.connection_string)

    def get_database_name(self) -> Optional[str]:
        if self.db_type == "mongodb":
            name = self.connection_string.rsplit("/", 1)[-1]
            return name or None
        return None

    def get_schema_info(self, query: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Returns full schema, or if `query` and LLM are provided,
        returns only the best-matching table/collection.
        """

        if self.schema_cache and not query:
            return self.schema_cache

        full = (
            self._load_postgres_schema()
            if self.db_type == "postgres"
            else self._load_mongodb_schema()
        )
        options = kwargs["options"] if "options" in kwargs else None

        if options:
            target_table = options.get("target_table", None)

            if target_table and full[target_table]:
                self.target = target_table
                print("target_table", target_table)
                return {target_table: full[target_table]}

        if query and self.llm:
            best = self._select_best(full, query)
            # print(f"Best match: {best}")
            return {best: full[best]}

        return full

    def _load_postgres_schema(self) -> Dict[str, Any]:
        schema = {}
        for table in self.inspector.get_table_names():
            cols = [
                {
                    "name": c["name"],
                    "type": str(c["type"]),
                    "nullable": c.get("nullable", True),
                }
                for c in self.inspector.get_columns(table)
            ]
            rels = [
                f"{table}.{fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}"
                for fk in self.inspector.get_foreign_keys(table)
            ]
            schema[table] = {"columns": cols, "relationships": rels}
        return schema

    def _load_mongodb_schema(self) -> Dict[str, Any]:
        db_name = self.get_database_name()
        if not db_name:
            raise ValueError("Missing MongoDB database name")

        db = self.client[db_name]
        schema = {}
        for col in db.list_collection_names():
            samples = list(db[col].find().limit(100))
            if not samples:
                continue
            fields = {}
            for doc in samples:
                for k, v in doc.items():
                    fields.setdefault(k, type(v).__name__)
            idxs = [
                str(i["key"]) for i in db[col].list_indexes() if i["name"] != "_id_"
            ]
            schema[col] = {
                "fields": [{"name": k, "type": t} for k, t in fields.items()],
                "indexes": idxs,
            }
        return schema

    def _select_best(self, options, query: str) -> str:
        opts = json.dumps(options)
        prompt = self.selection_prompt.format(options=opts, query=query)
        return self.llm.invoke(prompt).strip()
