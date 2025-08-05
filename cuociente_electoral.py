#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para calcular el cuociente electoral según las reglas colombianas
Autor: Juan Giraldo
Fecha: 2025
"""

import math
from typing import Dict, List, Tuple
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass
class Partido:
    """Clase para representar un partido político"""
    nombre: str
    votos: int
    curules_asignadas: int = 0
    residuo: float = 0.0


class CuocienteElectoral:
    """
    Clase para calcular el cuociente electoral según las reglas colombianas
    """
    
    def __init__(self, total_votos_validos: int, total_curules: int):
        """
        Inicializa el calculador de cuociente electoral
        
        Args:
            total_votos_validos: Total de votos válidos
            total_curules: Número total de curules a distribuir
        """
        self.total_votos_validos = total_votos_validos
        self.total_curules = total_curules
        self.partidos: List[Partido] = []
        
    def agregar_partido(self, nombre: str, votos: int):
        """Agrega un partido a la lista"""
        self.partidos.append(Partido(nombre=nombre, votos=votos))
    
    def calcular_cuociente_simple(self) -> float:
        """
        Calcula el cuociente electoral simple
        Cuociente = Total votos válidos / Total curules
        """
        if self.total_curules == 0:
            raise ValueError("El número de curules debe ser mayor a 0")
        return self.total_votos_validos / self.total_curules
    
    def calcular_cuociente_hare(self) -> float:
        """
        Calcula el cuociente electoral usando el método Hare
        Cuociente = Total votos válidos / Total curules
        """
        return self.calcular_cuociente_simple()
    
    def calcular_cuociente_droop(self) -> float:
        """
        Calcula el cuociente electoral usando el método Droop
        Cuociente = (Total votos válidos / (Total curules + 1)) + 1
        """
        if self.total_curules == 0:
            raise ValueError("El número de curules debe ser mayor a 0")
        return (self.total_votos_validos / (self.total_curules + 1)) + 1
    
    def asignar_curules_por_cuociente(self, metodo: str = "hare") -> Dict[str, int]:
        """
        Asigna curules usando el método especificado
        
        Args:
            metodo: "hare" o "droop"
            
        Returns:
            Diccionario con partido -> curules asignadas
        """
        if metodo.lower() == "hare":
            cuociente = self.calcular_cuociente_hare()
        elif metodo.lower() == "droop":
            cuociente = self.calcular_cuociente_droop()
        else:
            raise ValueError("Método debe ser 'hare' o 'droop'")
        
        # Reiniciar asignaciones
        for partido in self.partidos:
            partido.curules_asignadas = 0
            partido.residuo = 0.0
        
        # Primera asignación por cuociente
        curules_asignadas = 0
        for partido in self.partidos:
            curules_por_cuociente = int(partido.votos / cuociente)
            partido.curules_asignadas = curules_por_cuociente
            partido.residuo = partido.votos % cuociente
            curules_asignadas += curules_por_cuociente
        
        # Segunda asignación por residuos (método de mayor residuo)
        curules_restantes = self.total_curules - curules_asignadas
        
        if curules_restantes > 0:
            # Ordenar por residuo descendente
            partidos_ordenados = sorted(
                self.partidos, 
                key=lambda x: x.residuo, 
                reverse=True
            )
            
            # Asignar curules restantes a los partidos con mayor residuo
            for i in range(curules_restantes):
                if i < len(partidos_ordenados):
                    partidos_ordenados[i].curules_asignadas += 1
        
        return {partido.nombre: partido.curules_asignadas for partido in self.partidos}
    
    def calcular_porcentaje_votos(self, partido: Partido) -> float:
        """Calcula el porcentaje de votos de un partido"""
        if self.total_votos_validos == 0:
            return 0.0
        return (partido.votos / self.total_votos_validos) * 100
    
    def generar_reporte(self, metodo: str = "hare") -> str:
        """
        Genera un reporte completo de la distribución de curules
        
        Args:
            metodo: Método de cálculo ("hare" o "droop")
            
        Returns:
            String con el reporte formateado
        """
        asignacion = self.asignar_curules_por_cuociente(metodo)
        cuociente = self.calcular_cuociente_hare() if metodo == "hare" else self.calcular_cuociente_droop()
        
        reporte = f"""
{'='*60}
REPORTE DE DISTRIBUCIÓN DE CURULES - COLOMBIA
{'='*60}

DATOS GENERALES:
- Total votos válidos: {self.total_votos_validos:,}
- Total curules: {self.total_curules}
- Método utilizado: {metodo.upper()}
- Cuociente electoral: {cuociente:,.2f}

RESULTADOS POR PARTIDO:
{'-'*60}"""
        
        # Ordenar partidos por curules asignadas (descendente)
        partidos_ordenados = sorted(
            self.partidos, 
            key=lambda x: x.curules_asignadas, 
            reverse=True
        )
        
        for partido in partidos_ordenados:
            porcentaje = self.calcular_porcentaje_votos(partido)
            reporte += f"""
{partido.nombre.upper()}:
  - Votos: {partido.votos:,} ({porcentaje:.2f}%)
  - Curules asignadas: {partido.curules_asignadas}
  - Residuo: {partido.residuo:,.2f}"""
        
        # Resumen final
        total_curules_asignadas = sum(partido.curules_asignadas for partido in self.partidos)
        reporte += f"""

RESUMEN:
- Total curules asignadas: {total_curules_asignadas}
- Curules sin asignar: {self.total_curules - total_curules_asignadas}
{'='*60}"""
        
        return reporte


def ejemplo_uso():
    """Ejemplo de uso del script"""
    print("EJEMPLO DE CÁLCULO DE CUOCIENTE ELECTORAL COLOMBIANO")
    print("="*60)
    
    # Datos de ejemplo (elecciones ficticias)
    total_votos = 1000000
    total_curules = 10
    
    # Crear instancia del calculador
    calculador = CuocienteElectoral(total_votos, total_curules)
    
    # Agregar partidos con sus votos
    partidos_ejemplo = [
        ("Partido Liberal", 350000),
        ("Partido Conservador", 280000),
        ("Partido Verde", 150000),
        ("Centro Democrático", 120000),
        ("Polo Democrático", 80000),
        ("Otros partidos", 20000)
    ]
    
    for nombre, votos in partidos_ejemplo:
        calculador.agregar_partido(nombre, votos)
    
    # Generar reporte con método Hare
    print(calculador.generar_reporte("hare"))
    
    print("\n" + "="*60)
    print("COMPARACIÓN CON MÉTODO DROOP")
    print("="*60)
    
    # Generar reporte con método Droop
    print(calculador.generar_reporte("droop"))


def entrada_interactiva():
    """Función para entrada interactiva de datos"""
    print("CALCULADORA DE CUOCIENTE ELECTORAL COLOMBIANO")
    print("="*60)
    
    try:
        # Entrada de datos generales
        total_votos = int(input("Ingrese el total de votos válidos: "))
        total_curules = int(input("Ingrese el número total de curules: "))
        
        calculador = CuocienteElectoral(total_votos, total_curules)
        
        # Entrada de partidos
        print("\nIngrese los partidos y sus votos (deje nombre vacío para terminar):")
        
        while True:
            nombre = input("\nNombre del partido (o Enter para terminar): ").strip()
            if not nombre:
                break
                
            try:
                votos = int(input(f"Votos del partido '{nombre}': "))
                calculador.agregar_partido(nombre, votos)
            except ValueError:
                print("Error: Ingrese un número válido de votos")
                continue
        
        if not calculador.partidos:
            print("Error: Debe ingresar al menos un partido")
            return
        
        # Seleccionar método
        print("\nMétodos disponibles:")
        print("1. Hare (más común en Colombia)")
        print("2. Droop")
        
        metodo_opcion = input("Seleccione el método (1 o 2): ").strip()
        metodo = "hare" if metodo_opcion == "1" else "droop"
        
        # Generar reporte
        print(calculador.generar_reporte(metodo))
        
    except ValueError as e:
        print(f"Error en los datos ingresados: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        entrada_interactiva()
    else:
        ejemplo_uso() 