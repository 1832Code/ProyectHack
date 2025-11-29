-- ================================================
-- Script de Configuración de Base de Datos
-- Proyecto: ProyectHack - Sistema de Búsqueda Empresarial
-- ================================================

-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS search_db;
USE search_db;

-- ================================================
-- Tabla: components
-- Descripción: Almacena componentes de búsqueda y palabras clave
-- ================================================
CREATE TABLE IF NOT EXISTS components (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(255) NOT NULL UNIQUE,
    campo1 TEXT,           -- Resultado completo en JSON
    campo2 TEXT,           -- Descripción
    campo3 INT,            -- Relevance score
    campo4 TEXT,           -- Campo adicional (por definir)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_keyword (keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- Tabla: search_history
-- Descripción: Almacena el historial de búsquedas realizadas
-- ================================================
CREATE TABLE IF NOT EXISTS search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    country VARCHAR(100),
    sector VARCHAR(100),
    keywords JSON,         -- Array de palabras clave en formato JSON
    results JSON,          -- Resultados completos en formato JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company (company_name),
    INDEX idx_country (country),
    INDEX idx_sector (sector),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ================================================
-- Datos de Ejemplo (Opcional)
-- ================================================

-- Insertar algunos componentes de ejemplo
INSERT INTO components (keyword, campo1, campo2, campo3) VALUES
('tecnología', '{"keyword": "tecnología", "description": "Empresas del sector tecnológico", "relevance_score": 85}', 'Empresas del sector tecnológico', 85),
('innovación', '{"keyword": "innovación", "description": "Empresas innovadoras y disruptivas", "relevance_score": 90}', 'Empresas innovadoras y disruptivas', 90),
('sostenibilidad', '{"keyword": "sostenibilidad", "description": "Empresas con enfoque sostenible", "relevance_score": 80}', 'Empresas con enfoque sostenible', 80)
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- ================================================
-- Verificación
-- ================================================

-- Mostrar las tablas creadas
SHOW TABLES;

-- Verificar estructura de components
DESCRIBE components;

-- Verificar estructura de search_history
DESCRIBE search_history;

-- Contar registros en components
SELECT COUNT(*) as total_components FROM components;

-- Mostrar componentes de ejemplo
SELECT * FROM components;

-- ================================================
-- Información Adicional
-- ================================================

/*
INSTRUCCIONES DE USO:

1. Abrir MySQL Workbench o línea de comandos de MySQL
2. Ejecutar este script completo
3. Verificar que las tablas se hayan creado correctamente

COMANDOS ÚTILES:

-- Ver todas las bases de datos
SHOW DATABASES;

-- Usar la base de datos
USE search_db;

-- Ver todas las tablas
SHOW TABLES;

-- Eliminar la base de datos (¡CUIDADO!)
-- DROP DATABASE search_db;

-- Limpiar datos de las tablas
-- TRUNCATE TABLE components;
-- TRUNCATE TABLE search_history;

CONFIGURACIÓN EN main.py:

DB_CONFIG = {
    'host': 'localhost',
    'database': 'search_db',
    'user': 'root',
    'password': 'tu_password'  # ⚠️ Cambia esto
}
*/
