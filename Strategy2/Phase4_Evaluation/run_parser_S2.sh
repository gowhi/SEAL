#!/bin/bash
# run_parser_S2.sh
# Ejecuta el parser sobre todos los eval-S2-*.json de Strategy2/Phase4_Evaluation

EVAL_DIR="$HOME/Documentos/AIBench/Strategy2/Phase4_Evaluation"
PARSER="$EVAL_DIR/parser_promptfoo_csv.py"
OUTPUT_DIR="$EVAL_DIR/results"

cd "$EVAL_DIR" || exit 1
mkdir -p "$OUTPUT_DIR"

# Lista explícita de ficheros a procesar, con su prefijo de salida
declare -A FILES=(
    ["eval-S2-locals-run1-temp0.json"]="S2-locals-run1-temp0"
    ["eval-S2-locals-run2-temp0.json"]="S2-locals-run2-temp0"
    ["eval-S2-locals-run1-temp07.json"]="S2-locals-run1-temp07"
    ["eval-S2-locals-run2-temp07.json"]="S2-locals-run2-temp07"
    ["eval-S2-locals-run1-temp1.json"]="S2-locals-run1-temp1"
    ["eval-S2-locals-run2-temp1.json"]="S2-locals-run2-temp1"
    ["eval-S2-commercial-run1-temp0.json"]="S2-commercial-run1-temp0"
    ["eval-S2-commercial-run2-temp0.json"]="S2-commercial-run2-temp0"
    ["eval-S2-commercial-run1-temp07.json"]="S2-commercial-run1-temp07"
    ["eval-S2-commercial-run2-temp07.json"]="S2-commercial-run2-temp07"
)

for FILE in "${!FILES[@]}"; do
    PREFIX="${FILES[$FILE]}"
    if [ -f "$FILE" ]; then
        echo "==> Procesando $FILE  ->  prefijo: $PREFIX"
        python "$PARSER" "$FILE" "$PREFIX" "$OUTPUT_DIR"
    else
        echo "!! No encontrado: $FILE (saltando)"
    fi
done

echo ""
echo "Hecho. CSVs en: $OUTPUT_DIR"
ls -l "$OUTPUT_DIR"