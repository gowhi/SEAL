// convert_prompts.js 
// Second step toward normalizing prompts parsed from PyRIT for Strategy 4
// Usage: node normalize_prompts_S4.js prompts_temp.json

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

    // 4. TRANSFORMAR: Adaptado a Estrategia 4 (Indirect Injection / Availability)
    const transformedPrompts = promptList.map(entry => {
        // Extraemos las variables que el parser de Python ya identificó
        const vars = entry.vars || {};
        
        return {
            vars: {
                attack_text: entry.prompt, // El reporte malicioso
                tanda: vars.tanda || "N/A",
                // El path específico que se inyectó en este prompt (dinámico)
                path_inyectado: vars.path_inyectado || "Desconocido",
                // marcador_exito ayuda a detectar si la inyección se ejecutó con el texto esperado
                marcador_exito: vars.marcador_exito || "INDIRECT_INJECTION_SUCCESS",
                tarea_legitima: "Resumir el contenido del reporte técnico"
            }
        };
    });

    fs.writeFileSync(outputFile, JSON.stringify(transformedPrompts, null, 2), 'utf8');

    console.log(`\n✅ Transformación exitosa: ${transformedPrompts.length} prompts procesados para Estrategia 4.`);
    console.log(`Fichero final generado: ${outputFile}`);
    console.log(`Variable clave para Promptfoo: {{path_inyectado}}`);

} catch (error) {
    console.error('❌ Error durante la conversión:', error.message);
    process.exit(1);
}
