def import_all_models():
    """Import all models to register them with Base.metadata"""
    try:
        import base

        print("All models imported successfully")

    except ImportError as e:
        print(f"Error importing models: {e}")
        return {}


def get_registered_tables():
    """Get list of registered table names"""
    from .database import Base

    import_all_models()  # Ensure models are imported
    return list(Base.metadata.tables.keys())
