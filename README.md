# Calculadora de Cuociente Electoral Colombiano

Este script calcula el cuociente electoral según las reglas colombianas para la distribución de curules en elecciones.

## ¿Qué es el Cuociente Electoral?

El cuociente electoral es el número de votos necesarios para obtener una curul en una elección. En Colombia se utilizan principalmente dos métodos:

### Método Hare (Más común en Colombia)
```
Cuociente = Total votos válidos / Total curules
```

### Método Droop
```
Cuociente = (Total votos válidos / (Total curules + 1)) + 1
```

## Proceso de Asignación

1. **Primera asignación**: Se divide el número de votos de cada partido entre el cuociente electoral
2. **Segunda asignación**: Las curules restantes se asignan a los partidos con mayor residuo

## Uso del Script

### Ejecutar con ejemplo predefinido:
```powershell
python cuociente_electoral.py
```

### Ejecutar en modo interactivo:
```powershell
python cuociente_electoral.py --interactive
```

### Uso programático:
```python
from cuociente_electoral import CuocienteElectoral

# Crear calculador
calculador = CuocienteElectoral(total_votos=1000000, total_curules=10)

# Agregar partidos
calculador.agregar_partido("Partido A", 350000)
calculador.agregar_partido("Partido B", 280000)

# Generar reporte
reporte = calculador.generar_reporte("hare")
print(reporte)
```

## Reglas Colombianas Específicas

### Para Senado:
- 100 curules en total
- Se aplica el método Hare
- Umbral mínimo del 3% de votos válidos

### Para Cámara de Representantes:
- 166 curules en total
- Se aplica el método Hare
- Umbral mínimo del 3% de votos válidos

### Para Asambleas Departamentales:
- Número variable de curules según población
- Se aplica el método Hare
- Umbral mínimo del 3% de votos válidos

### Para Concejos Municipales:
- Número variable de curules según población
- Se aplica el método Hare
- Umbral mínimo del 3% de votos válidos

## Características del Script

- ✅ Cálculo automático del cuociente electoral
- ✅ Asignación de curules por cuociente y residuos
- ✅ Soporte para métodos Hare y Droop
- ✅ Generación de reportes detallados
- ✅ Modo interactivo para entrada de datos
- ✅ Validación de datos de entrada
- ✅ Cálculo de porcentajes de votos
- ✅ Ordenamiento por curules asignadas

## Ejemplo de Salida

```
============================================================
REPORTE DE DISTRIBUCIÓN DE CURULES - COLOMBIA
============================================================

DATOS GENERALES:
- Total votos válidos: 1,000,000
- Total curules: 10
- Método utilizado: HARE
- Cuociente electoral: 100,000.00

RESULTADOS POR PARTIDO:
------------------------------------------------------------

PARTIDO LIBERAL:
  - Votos: 350,000 (35.00%)
  - Curules asignadas: 3
  - Residuo: 50,000.00

PARTIDO CONSERVADOR:
  - Votos: 280,000 (28.00%)
  - Curules asignadas: 2
  - Residuo: 80,000.00

...

RESUMEN:
- Total curules asignadas: 10
- Curules sin asignar: 0
============================================================
```

## Requisitos

- Python 3.7 o superior
- No requiere dependencias externas

## Autor

Juan Giraldo - 2025

## Licencia

Este script es de uso libre para fines educativos y de análisis electoral. 