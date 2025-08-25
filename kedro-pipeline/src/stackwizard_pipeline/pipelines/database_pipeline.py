"""
Database initialization pipeline for StackWizard tests
"""
from kedro.pipeline import Pipeline, node, pipeline
from stackwizard_pipeline.nodes.database_init import (
    create_test_database,
    load_sql_schema,
    load_seed_data,
    verify_database,
    cleanup_test_database
)


def create_database_pipeline(**kwargs) -> Pipeline:
    """Create pipeline for database initialization with SQL files"""
    
    return pipeline(
        [
            node(
                func=create_test_database,
                inputs="parameters",
                outputs="db_info",
                name="create_database"
            ),
            node(
                func=load_sql_schema,
                inputs=["db_info", "parameters"],
                outputs="schema_info",
                name="load_schema"
            ),
            node(
                func=load_seed_data,
                inputs=["schema_info", "db_info", "parameters"],
                outputs="data_info",
                name="load_data"
            ),
            node(
                func=verify_database,
                inputs=["data_info", "db_info"],
                outputs="db_verification",
                name="verify_database"
            )
        ],
        namespace=None,
        inputs=None,
        outputs=None
    )


def create_database_cleanup_pipeline(**kwargs) -> Pipeline:
    """Create pipeline for database cleanup"""
    
    return pipeline(
        [
            node(
                func=cleanup_test_database,
                inputs=["db_verification", "parameters"],
                outputs="db_cleanup",
                name="cleanup_database"
            )
        ],
        namespace=None,
        inputs=None,
        outputs=None
    )