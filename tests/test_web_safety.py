def test_web_module_imports_and_exposes_no_api_post_routes():
    from marketloop.web import app, health

    info = health()
    assert info["mode"] == "paper-readonly-dashboard"

    api_routes = [route for route in app.routes if getattr(route, "path", "").startswith("/api/")]
    assert api_routes
    for route in api_routes:
        methods = getattr(route, "methods", set()) or set()
        assert "POST" not in methods
        assert "PUT" not in methods
        assert "DELETE" not in methods
