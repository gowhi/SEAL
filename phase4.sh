#!/bin/bash
# run_evals.sh
# Ejecuta promptfoo eval 2 veces por cada estrategia y registra en un único .txt

BASE_DIR="$HOME/Documentos/AIBench"
STRATEGIES=("Strategy1" "Strategy2" "Strategy3")
RUNS_PER_STRATEGY=2
LOG_FILE="$BASE_DIR/eval_runs_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "Log de ejecuciones - $(date)"
    echo "======================================"
} > "$LOG_FILE"

for STRATEGY in "${STRATEGIES[@]}"; do
    EVAL_DIR="$BASE_DIR/$STRATEGY/Phase4_Evaluation"

    if [ ! -d "$EVAL_DIR" ]; then
        echo "$STRATEGY | Run - | AVISO: directorio no encontrado ($EVAL_DIR)" | tee -a "$LOG_FILE"
        continue
    fi

    cd "$EVAL_DIR" || continue

    for RUN in $(seq 1 $RUNS_PER_STRATEGY); do
        TAG="${STRATEGY}_run${RUN}"
        START_TIME=$(date +'%Y-%m-%d %H:%M:%S')

        echo ""
        echo "==> $TAG - inicio: $START_TIME"

        TMP_OUTPUT=$(mktemp)

        # script escribe DIRECTO al archivo (no via pipe/tee) -> muestra la barra en pantalla
        # y guarda una copia limpia en TMP_OUTPUT, sin anidar pseudo-terminales
        script -qec "promptfoo eval -c promptfoo.yaml --no-cache --max-concurrency 1" "$TMP_OUTPUT"
        EXIT_CODE=$?

        END_TIME=$(date +'%Y-%m-%d %H:%M:%S')

        # Limpia códigos ANSI/retornos de carro antes de buscar el eval-ID
        CLEAN_OUTPUT=$(sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' -e 's/\r/\n/g' "$TMP_OUTPUT")
        EVAL_ID=$(echo "$CLEAN_OUTPUT" | grep -oP 'Starting evaluation \K\S+' | head -1)

        if [ -z "$EVAL_ID" ]; then
            EVAL_ID="NO_ENCONTRADO"
        fi

        if [ "$EXIT_CODE" -ne 0 ]; then
            ERROR_MSG="ERROR (exit code $EXIT_CODE)"
        else
            ERROR_MSG="OK"
        fi

        echo "$TAG | $EVAL_ID | inicio: $START_TIME | fin: $END_TIME | $ERROR_MSG" | tee -a "$LOG_FILE"

        rm -f "$TMP_OUTPUT"
    done
done

echo ""
echo "======================================" >> "$LOG_FILE"
echo "Resumen guardado en: $LOG_FILE"
cat "$LOG_FILE"