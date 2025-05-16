import sys
import logging
from typing import Tuple
from query_builder import QueryBuilder
from settings import db_config


def get_connection_string(db_type: str) -> str:
    if db_type == "postgres":
        return db_config.build_postgres_connection_string()
    if db_type == "mongodb":
        return db_config.get_mongodb_connection_string()
    raise ValueError("db_type must be 'postgres' or 'mongodb'")


def process(db_type: str, nl_query: str, **kwargs) -> Tuple[str, str]:
    conn = get_connection_string(db_type)
    print("Connecting to database...:", conn)
    qb = QueryBuilder(db_type, conn, llm_model="mistral:7b")
    print("Generating query for %s", nl_query)
    q = qb.generate_query(nl_query, **kwargs)

    print("Executing query...", q)
    res = qb.execute_query(q)

    print("Interpreting results", res)
    interp = qb.interpret_results(res, nl_query)
    return q, interp


def main(db_type: str, nl_query: str, **kwargs):
    try:
        q, interp = process(db_type, nl_query, **kwargs)
        print("Query:\n", nl_query)
        print("Result Interpretation:\n", interp)

    except Exception as e:
        print("Failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    # Example direct call
    main(
        db_type="postgres",
        nl_query="find all users",
        # options={"target_table": "Document"},
    )
