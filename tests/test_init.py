def test_pca_namespace():
    from pca import errors

    assert hasattr(errors, "ErrorBoundary")
    assert hasattr(errors, "error_builder")
    assert hasattr(errors, "ErrorCatalog")
    assert hasattr(errors, "ExceptionWithCode")
