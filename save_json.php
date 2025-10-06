<?php
header('Content-Type: application/json');

// Permitir CORS si es necesario
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'error' => 'Método no permitido']);
    exit;
}

$jsonFile = 'items.json';
$backupDir = 'backups';

try {
    // Leer el JSON enviado
    $newData = file_get_contents('php://input');
    $decodedData = json_decode($newData, true);
    
    // Validar que sea JSON válido
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception('JSON inválido: ' . json_last_error_msg());
    }
    
    // Crear directorio de backups si no existe
    if (!file_exists($backupDir)) {
        mkdir($backupDir, 0755, true);
    }
    
    // Crear backup del archivo actual
    if (file_exists($jsonFile)) {
        $timestamp = date('Y-m-d_H-i-s');
        $backupFile = $backupDir . '/items_backup_' . $timestamp . '.json';
        
        if (!copy($jsonFile, $backupFile)) {
            throw new Exception('No se pudo crear el backup');
        }
    } else {
        $backupFile = 'No existía archivo previo';
    }
    
    // Guardar el nuevo JSON
    if (file_put_contents($jsonFile, $newData) === false) {
        throw new Exception('No se pudo escribir el archivo');
    }
    
    echo json_encode([
        'success' => true,
        'backup' => $backupFile,
        'message' => 'Archivo guardado exitosamente'
    ]);
    
} catch (Exception $e) {
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>