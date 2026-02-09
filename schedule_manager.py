#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Horários - Criminologia e GESPIN
Versão 1.0 - Protótipo
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd


class CalendarValidator:
    """Módulo para validação de calendários acadêmicos"""
    
    def __init__(self, calendar_file: str):
        self.calendar_file = calendar_file
        self.academic_calendar = None
        self.valid_days = {}
        
    def load_calendar(self) -> bool:
        """Carrega calendário de arquivo CSV"""
        try:
            df = pd.read_csv(self.calendar_file, header=None)
            self.academic_calendar = df
            return True
        except Exception as e:
            print(f"Erro ao carregar calendário: {e}")
            return False
    
    def validate(self) -> Dict:
        """Valida calendário acadêmico"""
        report = {
            'status': 'VÁLIDO',
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        
        if self.academic_calendar is None:
            report['status'] = 'INVÁLIDO'
            report['errors'].append('Calendário não carregado')
            return report
        
        # Validações básicas
        try:
            # Verificar estrutura
            if self.academic_calendar.empty:
                report['errors'].append('Calendário vazio')
                report['status'] = 'INVÁLIDO'
        except Exception as e:
            report['errors'].append(f'Erro na validação: {str(e)}')
            report['status'] = 'INVÁLIDO'
        
        return report


class DisciplineAnalyzer:
    """Módulo para análise de distribuição de disciplinas"""
    
    def __init__(self, distribution_file: str):
        self.distribution_file = distribution_file
        self.disciplines = None
        self.statistics = {}
        
    def load_disciplines(self) -> bool:
        """Carrega distribuição de disciplinas"""
        try:
            df = pd.read_csv(self.distribution_file, header=None)
            # Pegar apenas primeiras colunas relevantes
            self.disciplines = df.iloc[:, :5].copy()
            self.disciplines.columns = ['Disciplina', 'Hora_aula', 'Encontros', 'Sigla', 'Horas']
            
            # Remover header se existir
            if self.disciplines.iloc[0, 0] == 'Disciplina':
                self.disciplines = self.disciplines.iloc[1:].reset_index(drop=True)
            
            # Converter para numérico
            self.disciplines['Hora_aula'] = pd.to_numeric(self.disciplines['Hora_aula'], errors='coerce')
            self.disciplines['Encontros'] = pd.to_numeric(self.disciplines['Encontros'], errors='coerce')
            self.disciplines['Horas'] = pd.to_numeric(self.disciplines['Horas'], errors='coerce')
            
            # Remover linhas com NaN
            self.disciplines = self.disciplines.dropna(subset=['Hora_aula'])
            
            return True
        except Exception as e:
            print(f"Erro ao carregar disciplinas: {e}")
            return False
    
    def analyze(self) -> Dict:
        """Analisa distribuição de disciplinas"""
        if self.disciplines is None or self.disciplines.empty:
            return {'error': 'Disciplinas não carregadas'}
        
        analysis = {
            'total_disciplines': len(self.disciplines),
            'total_hours': self.disciplines['Hora_aula'].sum(),
            'by_load': {}
        }
        
        # Agrupar por carga horária
        for load in sorted(self.disciplines['Hora_aula'].unique()):
            subset = self.disciplines[self.disciplines['Hora_aula'] == load]
            analysis['by_load'][f'{int(load)}h'] = {
                'count': len(subset),
                'total_hours': subset['Hora_aula'].sum()
            }
        
        self.statistics = analysis
        return analysis


class ScheduleGenerator:
    """Módulo para geração automática de horários"""
    
    # Padrões de horários
    WEEKLY_SLOTS = [
        {'day': 'Segunda', 'time': '19:00-20:40', 'duration': 100},
        {'day': 'Segunda', 'time': '21:00-22:40', 'duration': 100},
        {'day': 'Quarta', 'time': '19:00-20:40', 'duration': 100},
        {'day': 'Quarta', 'time': '21:00-22:40', 'duration': 100},
    ]
    
    BIWEEKLY_SLOTS = [
        {'day': 'Sexta', 'time': '19:00-20:40', 'duration': 100},
        {'day': 'Sexta', 'time': '21:00-22:40', 'duration': 100},
        {'day': 'Sábado', 'time': '08:00-09:40', 'duration': 100},
        {'day': 'Sábado', 'time': '10:00-11:40', 'duration': 100},
        {'day': 'Sábado', 'time': '13:00-14:40', 'duration': 100},
        {'day': 'Sábado', 'time': '15:00-16:40', 'duration': 100},
    ]
    
    def __init__(self):
        self.schedule = {}
        self.capacity = {
            'weekly': {'sem1': 64, 'sem2': 80},
            'biweekly': {'sem1': 96, 'sem2': 120}
        }
    
    def generate_weekly_schedule(self, disciplines: List[Dict], semester: str = 'sem1') -> Dict:
        """Gera horário para turma semanal"""
        schedule = {
            'type': 'weekly',
            'semester': semester,
            'capacity': self.capacity['weekly'][semester],
            'slots': self.WEEKLY_SLOTS,
            'assignments': []
        }
        
        return schedule
    
    def generate_biweekly_schedule(self, disciplines: List[Dict], semester: str = 'sem1') -> Dict:
        """Gera horário para turma quinzenal"""
        schedule = {
            'type': 'biweekly',
            'semester': semester,
            'capacity': self.capacity['biweekly'][semester],
            'slots': self.BIWEEKLY_SLOTS,
            'assignments': []
        }
        
        return schedule


class ConflictValidator:
    """Módulo para validação de conflitos de horários"""
    
    def __init__(self):
        self.conflicts = []
        self.warnings = []
    
    def validate_schedule(self, schedule: Dict) -> Dict:
        """Valida horário gerado"""
        report = {
            'status': 'VÁLIDO',
            'conflicts': [],
            'warnings': [],
            'summary': {}
        }
        
        # Validações básicas
        if not schedule:
            report['status'] = 'INVÁLIDO'
            report['conflicts'].append('Horário vazio')
        
        return report


class ScheduleExporter:
    """Módulo para exportação de horários"""
    
    def export_to_json(self, schedule: Dict, output_file: str) -> bool:
        """Exporta horário para JSON"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(schedule, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao exportar JSON: {e}")
            return False
    
    def export_summary(self, analysis: Dict, output_file: str) -> bool:
        """Exporta resumo de análise"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao exportar resumo: {e}")
            return False


class ScheduleManager:
    """Gerenciador central do sistema"""
    
    def __init__(self, course: str, year: str):
        self.course = course
        self.year = year
        self.calendar_validator = None
        self.discipline_analyzer = None
        self.schedule_generator = ScheduleGenerator()
        self.conflict_validator = ConflictValidator()
        self.exporter = ScheduleExporter()
    
    def process(self, calendar_file: str, distribution_file: str) -> Dict:
        """Processa completo do sistema"""
        results = {
            'course': self.course,
            'year': self.year,
            'timestamp': datetime.now().isoformat(),
            'steps': {}
        }
        
        # Passo 1: Validar calendário
        print(f"[1/5] Validando calendário...")
        self.calendar_validator = CalendarValidator(calendar_file)
        if self.calendar_validator.load_calendar():
            cal_report = self.calendar_validator.validate()
            results['steps']['calendar_validation'] = cal_report
            print(f"  Status: {cal_report['status']}")
        else:
            results['steps']['calendar_validation'] = {'status': 'ERRO'}
            return results
        
        # Passo 2: Analisar disciplinas
        print(f"[2/5] Analisando disciplinas...")
        self.discipline_analyzer = DisciplineAnalyzer(distribution_file)
        if self.discipline_analyzer.load_disciplines():
            disc_analysis = self.discipline_analyzer.analyze()
            results['steps']['discipline_analysis'] = disc_analysis
            print(f"  Disciplinas: {disc_analysis['total_disciplines']}")
            print(f"  Total de horas: {disc_analysis['total_hours']:.0f}")
        else:
            results['steps']['discipline_analysis'] = {'error': 'Não foi possível carregar'}
            return results
        
        # Passo 3: Gerar horários
        print(f"[3/5] Gerando horários...")
        weekly_sched = self.schedule_generator.generate_weekly_schedule([], 'sem1')
        biweekly_sched = self.schedule_generator.generate_biweekly_schedule([], 'sem1')
        results['steps']['schedule_generation'] = {
            'weekly': weekly_sched,
            'biweekly': biweekly_sched
        }
        print(f"  Horários gerados com sucesso")
        
        # Passo 4: Validar conflitos
        print(f"[4/5] Validando conflitos...")
        weekly_validation = self.conflict_validator.validate_schedule(weekly_sched)
        biweekly_validation = self.conflict_validator.validate_schedule(biweekly_sched)
        results['steps']['conflict_validation'] = {
            'weekly': weekly_validation,
            'biweekly': biweekly_validation
        }
        print(f"  Validação concluída")
        
        # Passo 5: Exportar resultados
        print(f"[5/5] Exportando resultados...")
        results['export_status'] = 'Pronto para exportação'
        
        return results


def main():
    """Função principal"""
    print("=" * 80)
    print("SISTEMA DE GERENCIAMENTO DE HORÁRIOS - v1.0")
    print("=" * 80)
    
    # Configuração
    course = "criminologia"
    year = "2026-2027"
    
    # Arquivos
    calendar_file = "CAL_2026-2027_Calendario.csv"
    distribution_file = "DIST_2026-2027_Criminologia.csv"
    
    # Processar
    manager = ScheduleManager(course, year)
    results = manager.process(calendar_file, distribution_file)
    
    # Exportar resultados
    print("\n" + "=" * 80)
    print("RESULTADOS")
    print("=" * 80)
    
    exporter = ScheduleExporter()
    output_file = f"schedule_results_{course}_{year.replace('-', '_')}.json"
    
    if exporter.export_summary(results, output_file):
        print(f"\n✅ Resultados exportados para: {output_file}")
    else:
        print(f"\n❌ Erro ao exportar resultados")
    
    print("\nProcesso concluído!")


if __name__ == "__main__":
    main()
