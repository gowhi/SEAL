const fs = require('fs');

// 1. Configuración de rutas
const inputFile = process.argv[2] || 'prompts_temp.json';
const outputFile = 'prompts_final_fixed.json';

if (!fs.existsSync(inputFile)) {
    console.error(`❌ Error: El archivo ${inputFile} no existe.`);
    process.exit(1);
}

try {
    // 2. Leer el contenido JSON generado por el parser de Python
    const rawData = fs.readFileSync(inputFile, 'utf8');
    const data = JSON.parse(rawData);

    // 3. Normalizar: Aceptar tanto un array directo como un objeto con clave 'prompts'
    const promptList = Array.isArray(data) ? data : (data.prompts || []);

    if (promptList.length === 0) {
        throw new Error('No se encontraron prompts en el archivo de entrada.');
    }

    // 4. TRANSFORMAR: Mapear "prompt" -> "vars.attack_text"
    const transformedPrompts = promptList.map(entry => {
        return {
            vars: {
                attack_text: entry.prompt, // El texto del ataque ahora es una variable
                tanda: entry.vars ? entry.vars.tanda : "N/A",
                path_esperado: entry.vars ? entry.vars.path_esperado : "N/A"
            }
        };
    });

    // 5. Guardar el resultado en formato JSON (compatible con promptfoo)
    fs.writeFileSync(outputFile, JSON.stringify(transformedPrompts, null, 2), 'utf8');

    console.log(`\n✅ Transformación exitosa: ${transformedPrompts.length} prompts procesados.`);
    console.log(`Fichero final generado: ${outputFile}`);

} catch (error) {
    console.error('❌ Error durante la conversión:', error.message);
    process.exit(1);
}
