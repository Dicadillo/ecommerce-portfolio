def assert_error_response(response, code, detail_field=None):
    assert set(response.data) == {"error"}
    error = response.data["error"]
    assert set(error) == {"codigo", "mensaje", "detalles"}
    assert error["codigo"] == code
    assert isinstance(error["mensaje"], str)
    assert error["mensaje"]
    assert isinstance(error["detalles"], dict)
    if detail_field is not None:
        assert detail_field in error["detalles"]
    return error
