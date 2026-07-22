#!/bin/bash
# run_parser_S3.sh
# Ejecuta el parser sobre todos los eval-S3-*.json

EVAL_DIR="$HOME/Documentos/AIBench/Strategy3/Phase4_Evaluation"
PARSER="$EVAL_DIR/parser_promptfoo_csv.py"
OUTPUT_DIR="$EVAL_DIR/results"

cd "$EVAL_DIR" || exit 1

mkdir -p "$OUTPUT_DIR"

declare -A FILES=(

["eval-S3-locals-run1-temp0.json"]="S3-locals-run1-temp0"
["eval-S3-locals-run2-temp0.json"]="S3-locals-run2-temp0"

["eval-S3-locals-run1-temp07.json"]="S3-locals-run1-temp07"
["eval-S3-locals-run2-temp07.json"]="S3-locals-run2-temp07"

["eval-S3-locals-run1-temp1.json"]="S3-locals-run1-temp1"
["eval-S3-locals-run2-temp1.json"]="S3-locals-run2-temp1"

["eval-S3-commercial-run1-temp0.json"]="S3-commercial-run1-temp0"
["eval-S3-commercial-run2-temp0.json"]="S3-commercial-run2-temp0"

["eval-S3-commercial-run1-temp07.json"]="S3-commercial-run1-temp07"
["eval-S3-commercial-run2-temp07.json"]="S3-commercial-run2-temp07"

["eval-S3-commercial-run1-temp1.json"]="S3-commercial-run1-temp1"
["eval-S3-commercial-run2-temp1.json"]="S3-commercial-run2-temp1"

)

for FILE in "${!FILES[@]}"; do

    PREFIX="${FILES[$FILE]}"

    if [ -f "$FILE" ]; then
        echo "==> Procesando $FILE -> $PREFIX"
        python "$PARSER" "$FILE" "$PREFIX" "$OUTPUT_DIR"
    else
        echo "!! No encontrado: $FILE"
    fi

done

echo ""
echo "CSVs generados en:"
echo "$OUTPUT_DIR"

ls -l "$OUTPUT_DIR"