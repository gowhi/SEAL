// =============================================================================
// convert_prompts.js
// =============================================================================
// Structural normalization script for Phase 3 of the SEAL pipeline.
// Reads the intermediate JSON output from parser_pyrit_to_promptfoo.py and
// transforms each entry into the variable-based schema required by Promptfoo.
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
        return {
            vars: {
                attack_text: entry.prompt, 
                tanda: entry.vars ? entry.vars.tanda : "N/A",
                path_esperado: entry.vars ? entry.vars.path_esperado : "N/A"
            }
        };
    });

    fs.writeFileSync(outputFile, JSON.stringify(transformedPrompts, null, 2), 'utf8');

    console.log(`\n✅ Transformación exitosa: ${transformedPrompts.length} prompts procesados.`);
    console.log(`Fichero final generado: ${outputFile}`);

} catch (error) {
    console.error('❌ Error durante la conversión:', error.message);
    process.exit(1);
}
