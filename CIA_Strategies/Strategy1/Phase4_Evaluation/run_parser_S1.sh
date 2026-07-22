#!/bin/bash
# run_parser_S1.sh
# Ejecuta el parser sobre todos los eval-S1-*.json de Strategy1/Phase4_Evaluation

EVAL_DIR="$HOME/Documentos/AIBench/Strategy1/Phase4_Evaluation"
PARSER="$EVAL_DIR/parser_promptfoo_csv.py"
OUTPUT_DIR="$EVAL_DIR/results"

cd "$EVAL_DIR" || exit 1
mkdir -p "$OUTPUT_DIR"

# Lista explícita de ficheros a procesar, con su prefijo de salida
declare -A FILES=(
    ["eval-S1-locals-run1-temp0.json"]="S1-locals-run1-temp0"
    ["eval-S1-locals-run2-temp0.json"]="S1-locals-run2-temp0"
    ["eval-S1-locals-run1-temp07.json"]="S1-locals-run1-temp07"
    ["eval-S1-locals-run2-temp07.json"]="S1-locals-run2-temp07"
    ["eval-S1-locals-run1-temp1.json"]="S1-locals-run1-temp1"
    ["eval-S1-locals-run2-temp1.json"]="S1-locals-run2-temp1"
    ["eval-S1-commercial-run1-temp0.json"]="S1-commercial-run1-temp0"
    ["eval-S1-commercial-run2-temp0.json"]="S1-commercial-run2-temp0"
    ["eval-S1-commercial-run1-temp07.json"]="S1-commercial-run1-temp07"
    ["eval-S1-commercial-run2-temp07.json"]="S1-commercial-run2-temp07"
    ["eval-S1-commercial-run1-temp1.json"]="S1-commercial-run1-temp1"
    ["eval-S1-commercial-run2-temp1.json"]="S1-commercial-run2-temp1"

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