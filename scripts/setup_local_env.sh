#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp -n .env.example .env 2>/dev/null || true
printf "\nEnvironnement Yeewde prêt.\n"
printf "Active le venv avec : source .venv/bin/activate\n"
