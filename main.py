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


def process(db_type: str, nl_query: str) -> Tuple[str, str]:
    conn = get_connection_string(db_type)
    print("Connecting to database...:", conn)
    qb = QueryBuilder(db_type, conn, llm_model="mistral:7b")
    print("Generating query for %s", nl_query)
    q = qb.generate_query(nl_query)

    print("Executing query...", q)
    res = qb.execute_query(q)

    print("Interpreting results")
    interp = qb.interpret_results(res, nl_query)
    return q, interp


def main(db_type: str, nl_query: str):
    try:
        q, interp = process(db_type, nl_query)
        print("Query:\n", nl_query)
        print("Result Interpretation:\n", interp)

    except Exception as e:
        print("Failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    # Example direct call
    main("postgres", "give me user list")


# conn = "postgresql://postgres:SmartonDev1998@dev.ckqxkzc9ymbp.ap-south-1.rds.amazonaws.com:5432/test"


# test db connection string for SQL
# from sqlalchemy import create_engine, MetaData, Table, select
# from sqlalchemy.exc import SQLAlchemyError
# import logging


# def get_all_users(conn_str: str):
#     try:
#         # Create engine and reflect metadata
#         engine = create_engine(conn_str)
#         metadata = MetaData()
#         user_table = Table("user", metadata, autoload_with=engine)

#         # Connect and execute the select query
#         with engine.connect() as conn:
#             result = conn.exec_driver_sql('SELECT id,username FROM "user"')
#             return result.fetchall()

#     except SQLAlchemyError as e:
#         logging.error(f"Error fetching users: {e}")
#         return []


# # Example usage:
# users = get_all_users(conn)
# print(users)
