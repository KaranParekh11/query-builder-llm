from typing import Optional
from urllib.parse import quote_plus
from decouple import config, UndefinedValueError


class DatabaseConfig:
    """Database configuration settings."""

    @staticmethod
    def build_postgres_connection_string(ssl_mode: Optional[str] = None) -> str:
        """
        Build a PostgreSQL connection string from environment variables.

        Args:
            ssl_mode: Optional SSL mode (e.g., 'require', 'verify-full', 'prefer')

        Returns:
            str: PostgreSQL connection string

        Raises:
            UndefinedValueError: If any required environment variable is missing
        """
        try:
            host = config("POSTGRES_HOST")
            port = config("POSTGRES_PORT", cast=int)
            database = config("POSTGRES_DATABASE")
            username = config("POSTGRES_USERNAME")
            password = config("POSTGRES_PASSWORD")

            # URL encode the password to handle special characters
            encoded_password = quote_plus(password)

            # Build the base connection string
            conn_string = (
                f"postgresql://{username}:{encoded_password}@{host}:{port}/{database}"
            )

            # Add SSL mode if specified
            if ssl_mode:
                conn_string += f"?sslmode={ssl_mode}"

            return conn_string
        except UndefinedValueError as e:
            raise ValueError(f"Missing required PostgreSQL configuration: {str(e)}")

    @staticmethod
    def get_mongodb_connection_string() -> str:
        """
        Get MongoDB connection string from environment variables.

        Returns:
            str: MongoDB connection string

        Raises:
            UndefinedValueError: If MONGODB_CONNECTION_STRING is not set
        """
        try:
            return config("MONGODB_CONNECTION_STRING")
        except UndefinedValueError:
            raise ValueError(
                "MONGODB_CONNECTION_STRING is not set in environment variables"
            )


# Create a global instance
db_config = DatabaseConfig()
