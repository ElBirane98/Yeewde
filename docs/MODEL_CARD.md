# Fiche modèle — OTIF LightGBM

- **Objectif** : prédire si une commande sera OTIF (1) ou non (0).
- **Algorithme** : LightGBM binaire, class_weight balanced.
- **Features** : quantités, coûts, délai standard, attributs pièce/fournisseur (sans fuite post-livraison).
- **Target** : `otif_score` (Gold `marts_otif_kpi`).
- **Tracking** : MLflow (`mlruns/`), artefact `mlruns/models/lgbm_otif.pkl`.
- **Limites** : classes déséquilibrées, données historiques figées, scoring batch.

Commandes :
```bash
python -m ml_engine.train
python -m ml_engine.evaluate
python -m ml_engine.drift_monitor
```
