from typing import Optional, Dict, Any, Union, List
from .postgres_builder import PostgresQueryBuilder
from .mongodb_builder import MongoDBQueryBuilder
from .schema_introspector import SchemaIntrospector
import pandas as pd


class QueryBuilder:
    """
    Unified interface for SQL or MongoDB query building and execution.
    """

    def __init__(
        self,
        db_type: str,
        connection_string: str,
        llm_model: Optional[str] = None,
        schema_cache: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        self.db_type = db_type.lower()
        self.introspector = SchemaIntrospector(
            db_type, connection_string, llm_model=llm_model, schema_cache=schema_cache
        )
        if self.db_type == "postgres":
            self.builder = PostgresQueryBuilder(self.introspector, llm_model)
        elif self.db_type == "mongodb":
            self.builder = MongoDBQueryBuilder(self.introspector, llm_model)
        else:
            raise ValueError(f"Unsupported db_type: {db_type}")

    def generate_query(self, nl: str, **kwargs) -> str:
        return self.builder.generate_query(nl, **kwargs)

    def execute_query(self, q: str) -> Union[pd.DataFrame, List[Dict[str, Any]]]:
        return self.builder.execute_query(q)

    def interpret_results(self, res, nl: str) -> str:
        return self.builder.interpret_results(res, nl)

    def get_schema(self, nl: Optional[str] = None) -> Dict[str, Any]:
        return self.introspector.get_schema_info(nl)
