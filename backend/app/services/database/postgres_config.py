"""
PostgreSQL Database Configuration
Connection settings for CMC Health database
"""

import os
from dataclasses import dataclass

@dataclass
class PostgresConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "cmc_health"
    user: str = "postgres"
    password: str = "gugan@2022"
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def asyncpg_dsn(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

# Global config instance
db_config = PostgresConfig(
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.getenv("POSTGRES_DB", "cmc_health"),
    user=os.getenv("POSTGRES_USER", "postgres"),
    password=os.getenv("POSTGRES_PASSWORD", "gugan@2022")
)
