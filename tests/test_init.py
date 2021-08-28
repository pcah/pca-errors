def test_pca_namespace():
    from pca import errors

    print("!!!", errors.__file__)

    assert hasattr(errors, "ExceptionWithCode")
    assert hasattr(errors, "ErrorCatalog")
