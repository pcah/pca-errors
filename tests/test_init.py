def test_pca_namespace():
    from pca import errors

    assert hasattr(errors, "ExceptionWithCode")
    assert hasattr(errors, "ErrorCatalog")
