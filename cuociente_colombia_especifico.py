#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script específico para calcular el cuociente electoral colombiano
con todas las reglas y umbrales específicos de Colombia
Autor: Juan Giraldo
Fecha: 2025
"""

from cuociente_electoral import CuocienteElectoral, Partido
from typing import Dict, List, Tuple
from enum import Enum


class TipoEleccion(Enum):
    """Tipos de elección en Colombia"""
    SENADO = "senado"
    CAMARA = "camara"
    ASAMBLEA = "asamblea"
    CONCEJO = "concejo"
    ALCALDIA = "alcaldia"


class CuocienteElectoralColombia(CuocienteElectoral):
    """
    Clase específica para calcular cuociente electoral según reglas colombianas
    """
    
    # Configuraciones específicas de Colombia
    CONFIGURACIONES = {
        TipoEleccion.SENADO: {
            "curules": 100,
            "umbral": 0.03,  # 3%
            "metodo": "hare"
        },
        TipoEleccion.CAMARA: {
            "curules": 166,
            "umbral": 0.03,  # 3%
            "metodo": "hare"
        },
        TipoEleccion.ASAMBLEA: {
            "curules": None,  # Variable según departamento
            "umbral": 0.03,  # 3%
            "metodo": "hare"
        },
        TipoEleccion.CONCEJO: {
            "curules": None,  # Variable según municipio
            "umbral": 0.03,  # 3%
            "metodo": "hare"
        },
        TipoEleccion.ALCALDIA: {
            "curules": 1,
            "umbral": 0.50,  # 50% + 1 voto
            "metodo": "mayoria"
        }
    }
    
    def __init__(self, tipo_eleccion: TipoEleccion, total_votos_validos: int, 
                 curules_personalizadas: int = None):
        """
        Inicializa el calculador para elecciones colombianas
        
        Args:
            tipo_eleccion: Tipo de elección (senado, cámara, etc.)
            total_votos_validos: Total de votos válidos
            curules_personalizadas: Número de curules (para asambleas/concejos)
        """
        config = self.CONFIGURACIONES[tipo_eleccion]
        
        if curules_personalizadas:
            total_curules = curules_personalizadas
        else:
            total_curules = config["curules"]
        
        super().__init__(total_votos_validos, total_curules)
        self.tipo_eleccion = tipo_eleccion
        self.umbral = config["umbral"]
        self.metodo_estandar = config["metodo"]
    
    def aplicar_umbral_minimo(self) -> List[Partido]:
        """
        Aplica el umbral mínimo del 3% (o 50% para alcaldías)
        Retorna solo los partidos que superan el umbral
        """
        votos_minimos = self.total_votos_validos * self.umbral
        partidos_calificados = []
        
        for partido in self.partidos:
            if partido.votos >= votos_minimos:
                partidos_calificados.append(partido)
        
        return partidos_calificados
    
    def calcular_mayoria_absoluta(self) -> Dict[str, int]:
        """
        Calcula ganador por mayoría absoluta (para alcaldías)
        """
        if not self.partidos:
            return {}
        
        # Ordenar por votos descendente
        partidos_ordenados = sorted(
            self.partidos, 
            key=lambda x: x.votos, 
            reverse=True
        )
        
        ganador = partidos_ordenados[0]
        votos_ganador = ganador.votos
        total_votos = self.total_votos_validos
        
        # Verificar si hay mayoría absoluta (50% + 1)
        if votos_ganador > (total_votos / 2):
            return {ganador.nombre: 1}
        else:
            # Si no hay mayoría absoluta, se va a segunda vuelta
            return {"SEGUNDA_VUELTA": 0}
    
    def asignar_curules_colombia(self) -> Dict[str, int]:
        """
        Asigna curules según las reglas específicas de Colombia
        """
        if self.tipo_eleccion == TipoEleccion.ALCALDIA:
            return self.calcular_mayoria_absoluta()
        
        # Aplicar umbral mínimo
        partidos_calificados = self.aplicar_umbral_minimo()
        
        if not partidos_calificados:
            return {}
        
        # Calcular cuociente solo con partidos que superan umbral
        votos_calificados = sum(p.votos for p in partidos_calificados)
        
        if self.metodo_estandar == "hare":
            cuociente = votos_calificados / self.total_curules
        else:
            cuociente = (votos_calificados / (self.total_curules + 1)) + 1
        
        # Asignar curules
        for partido in partidos_calificados:
            curules_por_cuociente = int(partido.votos / cuociente)
            partido.curules_asignadas = curules_por_cuociente
            partido.residuo = partido.votos % cuociente
        
        # Asignar curules restantes por residuos
        curules_asignadas = sum(p.curules_asignadas for p in partidos_calificados)
        curules_restantes = self.total_curules - curules_asignadas
        
        if curules_restantes > 0:
            partidos_ordenados = sorted(
                partidos_calificados, 
                key=lambda x: x.residuo, 
                reverse=True
            )
            
            for i in range(curules_restantes):
                if i < len(partidos_ordenados):
                    partidos_ordenados[i].curules_asignadas += 1
        
        return {partido.nombre: partido.curules_asignadas for partido in partidos_calificados}
    
    def generar_reporte_colombia(self) -> str:
        """
        Genera reporte específico para elecciones colombianas
        """
        if self.tipo_eleccion == TipoEleccion.ALCALDIA:
            return self._generar_reporte_alcaldia()
        
        asignacion = self.asignar_curules_colombia()
        partidos_calificados = self.aplicar_umbral_minimo()
        
        reporte = f"""
{'='*70}
REPORTE DE DISTRIBUCIÓN DE CURULES - {self.tipo_eleccion.value.upper()}
{'='*70}

DATOS GENERALES:
- Tipo de elección: {self.tipo_eleccion.value.upper()}
- Total votos válidos: {self.total_votos_validos:,}
- Total curules: {self.total_curules}
- Umbral mínimo: {self.umbral*100:.1f}%
- Método: {self.metodo_estandar.upper()}

PARTIDOS QUE SUPERAN EL UMBRAL ({self.umbral*100:.1f}%):
{'-'*70}"""
        
        # Mostrar partidos que superan umbral
        for partido in partidos_calificados:
            porcentaje = self.calcular_porcentaje_votos(partido)
            reporte += f"""
{partido.nombre.upper()}:
  - Votos: {partido.votos:,} ({porcentaje:.2f}%)
  - Curules asignadas: {partido.curules_asignadas}
  - Residuo: {partido.residuo:,.2f}"""
        
        # Mostrar partidos que NO superan umbral
        partidos_no_calificados = [p for p in self.partidos if p not in partidos_calificados]
        if partidos_no_calificados:
            reporte += f"""

PARTIDOS QUE NO SUPERAN EL UMBRAL:
{'-'*70}"""
            for partido in partidos_no_calificados:
                porcentaje = self.calcular_porcentaje_votos(partido)
                reporte += f"""
{partido.nombre.upper()}:
  - Votos: {partido.votos:,} ({porcentaje:.2f}%)
  - Estado: NO CALIFICA"""
        
        # Resumen final
        total_curules_asignadas = sum(partido.curules_asignadas for partido in partidos_calificados)
        reporte += f"""

RESUMEN:
- Partidos que superan umbral: {len(partidos_calificados)}
- Partidos que no superan umbral: {len(partidos_no_calificados)}
- Total curules asignadas: {total_curules_asignadas}
- Curules sin asignar: {self.total_curules - total_curules_asignadas}
{'='*70}"""
        
        return reporte
    
    def _generar_reporte_alcaldia(self) -> str:
        """Genera reporte específico para elección de alcaldía"""
        resultado = self.calcular_mayoria_absoluta()
        
        reporte = f"""
{'='*70}
REPORTE DE ELECCIÓN DE ALCALDÍA - COLOMBIA
{'='*70}

DATOS GENERALES:
- Tipo de elección: ALCALDÍA
- Total votos válidos: {self.total_votos_validos:,}
- Umbral para mayoría absoluta: 50% + 1 voto
- Votos necesarios para ganar: {self.total_votos_validos // 2 + 1:,}

RESULTADOS:
{'-'*70}"""
        
        # Ordenar por votos
        partidos_ordenados = sorted(
            self.partidos, 
            key=lambda x: x.votos, 
            reverse=True
        )
        
        for i, partido in enumerate(partidos_ordenados):
            porcentaje = self.calcular_porcentaje_votos(partido)
            reporte += f"""
{i+1}. {partido.nombre.upper()}:
    - Votos: {partido.votos:,} ({porcentaje:.2f}%)
    - Estado: {'GANADOR' if partido.nombre in resultado else 'PERDEDOR'}"""
        
        if "SEGUNDA_VUELTA" in resultado:
            reporte += f"""

RESULTADO: SEGUNDA VUELTA REQUERIDA
Ningún candidato obtuvo mayoría absoluta (50% + 1 voto)
{'='*70}"""
        else:
            ganador = list(resultado.keys())[0]
            reporte += f"""

RESULTADO: GANADOR POR MAYORÍA ABSOLUTA
{ganador.upper()} es el alcalde electo
{'='*70}"""
        
        return reporte


def ejemplo_senado():
    """Ejemplo de cálculo para Senado"""
    print("EJEMPLO: ELECCIÓN DE SENADO - COLOMBIA")
    print("="*70)
    
    # Datos ficticios de elección de Senado
    total_votos = 25000000  # 25 millones de votos
    curules = 100
    
    calculador = CuocienteElectoralColombia(
        tipo_eleccion=TipoEleccion.SENADO,
        total_votos_validos=total_votos
    )
    
    # Partidos con sus votos
    partidos_senado = [
        ("Partido Liberal", 8500000),
        ("Partido Conservador", 7200000),
        ("Centro Democrático", 3800000),
        ("Partido Verde", 2200000),
        ("Polo Democrático", 1800000),
        ("FARC", 800000),
        ("Partido de la U", 600000),
        ("Cambio Radical", 400000),
        ("Otros partidos menores", 2000000)
    ]
    
    for nombre, votos in partidos_senado:
        calculador.agregar_partido(nombre, votos)
    
    print(calculador.generar_reporte_colombia())


def ejemplo_alcaldia():
    """Ejemplo de cálculo para Alcaldía"""
    print("\n" + "="*70)
    print("EJEMPLO: ELECCIÓN DE ALCALDÍA - COLOMBIA")
    print("="*70)
    
    # Datos ficticios de elección de alcaldía
    total_votos = 500000  # 500 mil votos
    
    calculador = CuocienteElectoralColombia(
        tipo_eleccion=TipoEleccion.ALCALDIA,
        total_votos_validos=total_votos
    )
    
    # Candidatos a alcaldía
    candidatos = [
        ("Juan Pérez", 180000),
        ("María García", 160000),
        ("Carlos López", 120000),
        ("Ana Rodríguez", 40000)
    ]
    
    for nombre, votos in candidatos:
        calculador.agregar_partido(nombre, votos)
    
    print(calculador.generar_reporte_colombia())


def entrada_interactiva_colombia():
    """Entrada interactiva para elecciones colombianas"""
    print("CALCULADORA DE CUOCIENTE ELECTORAL - COLOMBIA")
    print("="*70)
    
    try:
        # Seleccionar tipo de elección
        print("\nTipos de elección disponibles:")
        for i, tipo in enumerate(TipoEleccion, 1):
            print(f"{i}. {tipo.value.upper()}")
        
        opcion = int(input("\nSeleccione el tipo de elección (1-5): "))
        tipo_eleccion = list(TipoEleccion)[opcion - 1]
        
        # Entrada de datos
        total_votos = int(input("\nIngrese el total de votos válidos: "))
        
        curules_personalizadas = None
        if tipo_eleccion in [TipoEleccion.ASAMBLEA, TipoEleccion.CONCEJO]:
            curules_personalizadas = int(input("Ingrese el número de curules: "))
        
        calculador = CuocienteElectoralColombia(
            tipo_eleccion=tipo_eleccion,
            total_votos_validos=total_votos,
            curules_personalizadas=curules_personalizadas
        )
        
        # Entrada de partidos/candidatos
        print(f"\nIngrese los partidos/candidatos y sus votos:")
        
        while True:
            nombre = input("\nNombre del partido/candidato (o Enter para terminar): ").strip()
            if not nombre:
                break
                
            try:
                votos = int(input(f"Votos de '{nombre}': "))
                calculador.agregar_partido(nombre, votos)
            except ValueError:
                print("Error: Ingrese un número válido de votos")
                continue
        
        if not calculador.partidos:
            print("Error: Debe ingresar al menos un partido/candidato")
            return
        
        # Generar reporte
        print(calculador.generar_reporte_colombia())
        
    except ValueError as e:
        print(f"Error en los datos ingresados: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        entrada_interactiva_colombia()
    else:
        ejemplo_senado()
        ejemplo_alcaldia() 