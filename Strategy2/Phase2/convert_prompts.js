// Second step toward normalizing prompts parsed from PyRIT for Strategy 2

const fs = require('fs');

// 1. Configuración de rutas
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

    // 4. TRANSFORMAR: Adaptado a Estrategia 2 (Confidencialidad)
    const transformedPrompts = promptList.map(entry => {
        return {
            vars: {
                attack_text: entry.prompt,
                tanda: entry.vars ? entry.vars.tanda : "N/A",
                // Cambiamos path_esperado por el secreto y la variable del system prompt
                secreto_esperado: "AI_SECURITY_2025",
                variable_buscada: "SECRET_API_KEY"
            }
        };
    });

    fs.writeFileSync(outputFile, JSON.stringify(transformedPrompts, null, 2), 'utf8');

    console.log(`\n✅ Transformación exitosa: ${transformedPrompts.length} prompts procesados para Estrategia 2.`);
    console.log(`Fichero final generado: ${outputFile}`);

} catch (error) {
    console.error('❌ Error durante la conversión:', error.message);
    process.exit(1);
}