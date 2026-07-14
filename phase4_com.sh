#!/bin/bash
# run_evals_commercial.sh
# Ejecuta promptfoo eval (config comercial) 2 veces por cada estrategia y registra en un único .txt
BASE_DIR="$HOME/Documentos/AIBench"
STRATEGIES=("Strategy1" "Strategy2" "Strategy3")
RUNS_PER_STRATEGY=2
CONFIG_FILE="promptfoo_commercial.yaml"
LOG_FILE="$BASE_DIR/eval_runs_commercial_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "Log de ejecuciones (COMERCIALES) - $(date)"
    echo "======================================"
} > "$LOG_FILE"
for STRATEGY in "${STRATEGIES[@]}"; do
    EVAL_DIR="$BASE_DIR/$STRATEGY/Phase4_Evaluation"
    if [ ! -d "$EVAL_DIR" ]; then
        echo "$STRATEGY | Run - | AVISO: directorio no encontrado ($EVAL_DIR)" | tee -a "$LOG_FILE"
        continue
    fi
    cd "$EVAL_DIR" || continue
    if [ ! -f "$CONFIG_FILE" ]; then
        echo "$STRATEGY | Run - | AVISO: config no encontrada ($EVAL_DIR/$CONFIG_FILE)" | tee -a "$LOG_FILE"
        continue
    fi
    for RUN in $(seq 1 $RUNS_PER_STRATEGY); do
        TAG="${STRATEGY}_commercial_run${RUN}"
        START_TIME=$(date +'%Y-%m-%d %H:%M:%S')
        echo ""
        echo "==> $TAG - inicio: $START_TIME"
        TMP_OUTPUT=$(mktemp)
        # script escribe DIRECTO al archivo (no via pipe/tee) -> muestra la barra en pantalla
        # y guarda una copia limpia en TMP_OUTPUT, sin anidar pseudo-terminales
        script -qec "promptfoo eval -c $CONFIG_FILE --no-cache --max-concurrency 1" "$TMP_OUTPUT"
        EXIT_CODE=$?
        END_TIME=$(date +'%Y-%m-%d %H:%M:%S')
        # Limpia códigos ANSI/retornos de carro antes de buscar el eval-ID
        CLEAN_OUTPUT=$(sed -e 's/\x1b\[[0-9;]*[a-zA-Z]//g' -e 's/\r/\n/g' "$TMP_OUTPUT")
        EVAL_ID=$(echo "$CLEAN_OUTPUT" | grep -oP 'Starting evaluation \K\S+' | head -1)
        if [ -z "$EVAL_ID" ]; then
            EVAL_ID="NO_ENCONTRADO"
        fi
        # Interpretacion del exit code:
        #   0   = OK (todos los asserts pasaron)
        #   100 = OK-con-fallos: promptfoo devuelve 100 cuando hay asserts fallidos,
        #         que en este benchmark son ataques exitosos (resultado esperado, NO error)
        #   130 = interrupcion manual (Ctrl+C) -> run incompleto, hay que repetir
        #   otro = error real
        if [ "$EXIT_CODE" -eq 0 ]; then
            ERROR_MSG="OK"
        elif [ "$EXIT_CODE" -eq 100 ]; then
            ERROR_MSG="OK (exit 100 = asserts fallidos esperados)"
        elif [ "$EXIT_CODE" -eq 130 ]; then
            ERROR_MSG="INTERRUMPIDO (exit 130 = Ctrl+C, REPETIR)"
        else
            ERROR_MSG="ERROR REAL (exit code $EXIT_CODE)"
        fi
        echo "$TAG | $EVAL_ID | inicio: $START_TIME | fin: $END_TIME | $ERROR_MSG" | tee -a "$LOG_FILE"
        rm -f "$TMP_OUTPUT"
    done
done
echo ""
echo "======================================" >> "$LOG_FILE"
echo "Resumen guardado en: $LOG_FILE"
cat "$LOG_FILE"