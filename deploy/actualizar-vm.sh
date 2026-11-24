#!/usr/bin/env bash
# Actualiza DocuMind en la VM. Uso: cd ~/documind && ./deploy/actualizar-vm.sh
set -euo pipefail

ZIP="${ZIP:-$HOME/dist-frontend.zip}"
DOMINIO="${DOMINIO:-documindcloud.duckdns.org}"
cd "$(dirname "$0")/.."

echo "== Disco y memoria"
df -h / | tail -1
free -h | sed -n 1,2p
libre=$(df --output=avail -m / | tail -1 | tr -d ' ')
if [ "$libre" -lt 500 ]; then
  echo "Menos de 500 MB libres, se limpia la cache de construccion"
  docker builder prune -f
fi

echo "== Comprobaciones previas"
[ -f "$ZIP" ] || { echo "Falta $ZIP, subelo con el engranaje del SSH"; exit 1; }
[ -f .env ] || { echo "Falta .env en $(pwd)"; exit 1; }
grep -q '^GEMINI_API_KEY=.\+' .env || { echo "GEMINI_API_KEY vacia en .env"; exit 1; }
grep -q '^FIREBASE_PROJECT_ID=.\+' .env || { echo "FIREBASE_PROJECT_ID vacio en .env"; exit 1; }
docker network inspect edge >/dev/null 2>&1 || docker network create edge

echo "== Codigo"
git pull --ff-only
git log --oneline -1

echo "== Frontend compilado"
rm -rf frontend/dist
python3 -m zipfile -e "$ZIP" frontend/
[ -f frontend/dist/frontend/browser/index.html ] || { echo "El zip no trae dist/frontend/browser"; exit 1; }

echo "== Contenedores"
docker compose -f docker-compose.yml -f docker-compose.vm.yml up -d --build

echo "== Espera del backend"
for i in $(seq 1 40); do
  if curl -fsS http://127.0.0.1:8081/api/health >/dev/null 2>&1; then
    echo "backend responde"
    break
  fi
  sleep 3
done
curl -fsS http://127.0.0.1:8081/api/health || { docker logs --tail 40 documind-backend; exit 1; }
echo

echo "== Publico"
curl -s -o /dev/null -w "documind %{http_code}\n" "https://$DOMINIO/api/health" || true
curl -s -o /dev/null -w "movifi %{http_code}\n" https://movifi.duckdns.org/api/health || true

echo "== Contenedores en marcha"
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'documind|movifi|NAMES' || true
echo
echo "Indexando el corpus nuevo, unos 50 minutos. Seguimiento:"
echo "  docker logs -f documind-backend"
echo "  docker exec documind-backend sh -c 'wc -l /app/data/embeddings.jsonl'"
echo "Total esperado: 6212 trozos"
