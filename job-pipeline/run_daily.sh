#!/usr/bin/env bash
# Lancement quotidien de la veille emploi.
# Cree l'environnement virtuel au premier appel, puis execute le pipeline.
#
#   ./run_daily.sh              # veille complete
#   ./run_daily.sh --only-new   # ne rapporter que les nouveautes
#
# Le script est concu pour cron / systemd / launchd : il n'ecrit rien sur la
# sortie standard en cas de succes silencieux, tout va dans logs/.

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

VENV="${JOBWATCH_VENV:-$DIR/.venv}"
PYTHON="${JOBWATCH_PYTHON:-python3}"
LOG_DIR="$DIR/logs"
mkdir -p "$LOG_DIR"

if [ ! -x "$VENV/bin/python" ]; then
    echo "Creation de l'environnement virtuel dans $VENV"
    "$PYTHON" -m venv "$VENV"
    "$VENV/bin/pip" install --quiet --upgrade pip
    "$VENV/bin/pip" install --quiet -r "$DIR/requirements.txt"
fi

STAMP="$(date +%Y-%m-%d)"
exec "$VENV/bin/python" -m jobwatch \
    --config "$DIR/config.yaml" \
    --log-file "$LOG_DIR/jobwatch-$STAMP.log" \
    run "$@"
