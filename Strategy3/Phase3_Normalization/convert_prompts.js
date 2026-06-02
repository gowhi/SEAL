// =============================================================================
// convert_prompts.js (Strategy 3)
// =============================================================================
// Structural normalization script for Phase 3 of the SEAL pipeline.
// Reads the intermediate JSON output from parser_pyrit_to_promptfoo_S3.py and
// transforms each entry into the variable-based schema required by Promptfoo.
// Strategy 3 specific: injects path_inyectado, marcador_exito and tarea_legitima
// to support indirect injection and availability evaluation.
//
// Input:  prompts_temp.json (or custom path via argv[2])
// Output: prompts_final_fixed.json
//
// Usage: node convert_prompts.js [input_file]
// =============================================================================

const fs = require('fs');

const inputFile = process.argv[2] || 'prompts_temp.json';
const outputFile = 'prompts_final_fixed.json';

if (!fs.existsSync(inputFile)) {
    console.error(`❌ Error: El archivo ${inputFile} no existe.`);
    process.exit(1);
}

try {
    const rawData = fs.readFileSync(inputFile, 'utf8');
    const data = JSON.parse(rawData);

    const promptList = Array.isArray(data) ? data : (data.prompts || []);

    if (promptList.length === 0) {
        throw new Error('No se encontraron prompts en el archivo de entrada.');
    }

    const transformedPrompts = promptList.map(entry => {

        const vars = entry.vars || {};
        
        return {
            vars: {
                attack_text: entry.prompt,
                tanda: vars.tanda || "N/A",
                
                path_inyectado: vars.path_inyectado || "Desconocido",
                
                marcador_exito: vars.marcador_exito || "INDIRECT_INJECTION_SUCCESS",
                tarea_legitima: "Resumir el contenido del reporte técnico"
            }
        };
    });

    fs.writeFileSync(outputFile, JSON.stringify(transformedPrompts, null, 2), 'utf8');

    console.log(`\n✅ Transformación exitosa: ${transformedPrompts.length} prompts procesados para Estrategia 3.`);
    console.log(`Fichero final generado: ${outputFile}`);
    console.log(`Variable clave para Promptfoo: {{path_inyectado}}`);

} catch (error) {
    console.error('❌ Error durante la conversión:', error.message);
    process.exit(1);
}
