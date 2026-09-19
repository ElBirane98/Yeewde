import dagster_orchestrator.definitions as d


def test_dagster_defs_loads():
    assert d.defs is not None
    asset_keys = {str(k) for k in d.defs.get_asset_graph().get_all_asset_keys()}
    assert asset_keys
