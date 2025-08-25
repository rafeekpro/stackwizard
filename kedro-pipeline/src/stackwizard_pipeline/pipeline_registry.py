"""
Project pipelines registry
"""
from typing import Dict
from kedro.pipeline import Pipeline
from stackwizard_pipeline.pipelines import validation_pipeline, test_pipeline, database_pipeline


def register_pipelines() -> Dict[str, Pipeline]:
    """Register project pipelines.
    
    Returns:
        A mapping from pipeline names to Pipeline objects.
    """
    
    # Create all pipeline variants
    validation = validation_pipeline.create_validation_pipeline()
    quick_test = validation_pipeline.create_quick_test_pipeline()
    release = validation_pipeline.create_release_pipeline()
    
    # New comprehensive test pipelines
    package_tests = test_pipeline.create_package_test_pipeline()
    structure_tests = test_pipeline.create_structure_test_pipeline()
    docker_tests = test_pipeline.create_docker_test_pipeline()
    e2e_tests = test_pipeline.create_e2e_test_pipeline()
    full_tests = test_pipeline.create_full_test_pipeline()
    
    # Database pipelines
    db_init = database_pipeline.create_database_pipeline()
    db_cleanup = database_pipeline.create_database_cleanup_pipeline()
    
    return {
        # Default pipeline runs full validation
        "__default__": validation,
        
        # Original pipelines
        "validation": validation,
        "quick": quick_test,
        "release": release,
        
        # New test pipelines
        "test:package": package_tests,
        "test:structure": structure_tests,
        "test:docker": docker_tests,
        "test:e2e": e2e_tests,
        "test:all": full_tests,
        
        # Database pipelines
        "db:init": db_init,
        "db:cleanup": db_cleanup,
        "db:full": db_init + db_cleanup,
    }