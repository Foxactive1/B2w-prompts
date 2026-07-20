"""Smoke tests: garantem que os apps sobem e respondem em modo mock (sem GROQ_API_KEY)."""
import importlib

import pytest

APP_MODULES = ["app", "app_v2", "app_v3", "newfile"]


@pytest.fixture(autouse=True)
def _no_groq_key(monkeypatch):
    # Força o modo offline/mock removendo a chave da Groq.
    monkeypatch.delenv("GROQ_API_KEY", raising=False)


@pytest.mark.parametrize("module_name", APP_MODULES)
def test_home_route_ok(module_name):
    module = importlib.import_module(module_name)
    client = module.app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_app_v3_full_flow_mock():
    module = importlib.import_module("app_v3")
    client = module.app.test_client()

    client.post(
        "/create",
        data={
            "client_name": "Acme",
            "industry": "Varejo",
            "area": "Processos lentos",
            "context": "Empresa media",
            "objective": "Reduzir custos",
        },
    )

    scope = client.get("/scope")
    assert scope.status_code == 200

    regenerate = client.post("/api/regenerate", json={"section": "roi"})
    assert regenerate.status_code == 200
    assert "content" in regenerate.get_json()
