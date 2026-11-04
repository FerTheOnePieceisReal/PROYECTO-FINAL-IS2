
# Actividad 4 - Pruebas de Repositorio

## Módulo seleccionado
Persistencia de usuarios (User) mediante SQLAlchemy.

## Objetivo
Verificar las operaciones de almacenamiento, consulta,
actualización y eliminación de usuarios, así como
las restricciones de integridad de la base de datos.

## Casos de prueba

| Método / Operación | Caso de prueba | Valores de prueba | Resultado esperado |
|---|---|---|---|
| INSERT | Insertar usuario | joaquin / joaquin@example.com | Usuario almacenado con ID |
| SELECT | Buscar por ID | ID de alice | Retorna el usuario correcto |
| SELECT | Buscar ID inexistente | 9999 | Retorna None |
| UPDATE | Actualizar usuario | carlos a carlos_actualizado | Nombre actualizado |
| DELETE | Eliminar usuario | ID de maria | Usuario eliminado |
| INSERT | Correo duplicado | duplicado@example.com | IntegrityError |

## Herramientas utilizadas
- Python 3.11.9
- unittest
- SQLAlchemy
- SQLite en memoria
- coverage.py

## Resultados
- Pruebas ejecutadas: 6
- Pruebas aprobadas: 6
- Errores: 0
- Cobertura global reportada: 47%
- Cobertura de app/models.py: 57%

Nota: La cobertura corresponde al código medido durante la
ejecución de estas pruebas, no exclusivamente a las operaciones
de persistencia de usuarios.
