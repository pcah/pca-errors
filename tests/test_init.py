def test_pca_namespace():
    from pca.packages import errors

    assert hasattr(errors, "VERSION")
    assert hasattr(errors, "ErrorBoundary")
    assert hasattr(errors, "error_builder")
    assert hasattr(errors, "ErrorMeta")
    assert hasattr(errors, "ErrorCatalog")
    assert hasattr(errors, "ExceptionWithCode")
