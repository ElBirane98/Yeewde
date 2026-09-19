import dagster_orchestrator.definitions as d

print('IMPORT_OK')
print(sorted(str(k) for k in d.defs.get_asset_graph().get_all_asset_keys()))
