#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Gerenciamento de Feriados e Pontos Facultativos
Integrado ao Sistema de Gerenciamento de Horários
"""

from datetime import datetime
from typing import Dict, List, Tuple
import re


class HolidayManager:
    """Gerencia feriados e pontos facultativos"""
    
    def __init__(self, holidays_file: str = None):
        self.holidays_file = holidays_file
        self.holidays = {}
        self.optional_holidays = {}
        self.load_holidays()
    
    def load_holidays(self):
        """Carrega lista de feriados e pontos facultativos"""
        if not self.holidays_file:
            self._load_default_holidays()
            return
        
        try:
            with open(self.holidays_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines[1:]:  # Skip header
                if not line.strip():
                    continue
                
                self._parse_holiday_line(line.strip())
        except Exception as e:
            print(f"Erro ao carregar feriados: {e}")
            self._load_default_holidays()
    
    def _parse_holiday_line(self, line: str):
        """Parse uma linha de feriado"""
        try:
            # Formato: "DD de mês - dia da semana, descrição (tipo)"
            # Exemplo: "21 de abril - terça-feira, Tiradentes (feriado nacional);"
            
            # Extrair data
            match = re.match(r'(\d+)\s+de\s+(\w+)', line)
            if not match:
                return
            
            day = int(match.group(1))
            month_name = match.group(2).lower()
            
            # Converter nome do mês para número
            months = {
                'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4,
                'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
                'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
            }
            
            month = months.get(month_name)
            if not month:
                return
            
            # Extrair tipo de feriado
            is_optional = 'ponto facultativo' in line.lower()
            
            # Extrair descrição
            desc_match = re.search(r',\s*([^(]+)\s*\(', line)
            description = desc_match.group(1).strip() if desc_match else "Feriado"
            
            # Armazenar
            date_key = f"{day:02d}/{month:02d}"
            
            if is_optional:
                self.optional_holidays[date_key] = description
            else:
                self.holidays[date_key] = description
        
        except Exception as e:
            print(f"Erro ao processar linha: {line} - {e}")
    
    def _load_default_holidays(self):
        """Carrega feriados padrão de 2026"""
        self.holidays = {
            '01/01': 'Confraternização Universal',
            '03/04': 'Sexta-feira Santa',
            '21/04': 'Tiradentes',
            '01/05': 'Dia Mundial do Trabalho',
            '07/09': 'Independência do Brasil',
            '12/10': 'Nossa Senhora Aparecida',
            '02/11': 'Finados',
            '15/11': 'Proclamação da República',
            '20/11': 'Dia da Consciência Negra',
            '25/12': 'Natal',
        }
        
        self.optional_holidays = {
            '02/01': 'Ponto Facultativo',
            '16/02': 'Carnaval',
            '17/02': 'Carnaval',
            '18/02': 'Quarta-feira de Cinzas',
            '02/04': 'Quinta-feira Santa',
            '20/04': 'Ponto Facultativo',
            '04/06': 'Corpus Christi',
            '05/06': 'Ponto Facultativo',
            '15/08': 'Assunção de Nossa Senhora',
            '30/10': 'Dia do Servidor Público',
            '07/12': 'Imaculada Conceição',
            '08/12': 'Imaculada Conceição',
            '24/12': 'Ponto Facultativo',
            '31/12': 'Ponto Facultativo',
        }
    
    def is_holiday(self, date: datetime) -> bool:
        """Verifica se é feriado"""
        date_key = date.strftime('%d/%m')
        return date_key in self.holidays
    
    def is_optional_holiday(self, date: datetime) -> bool:
        """Verifica se é ponto facultativo"""
        date_key = date.strftime('%d/%m')
        return date_key in self.optional_holidays
    
    def get_holiday_name(self, date: datetime) -> str:
        """Retorna nome do feriado"""
        date_key = date.strftime('%d/%m')
        
        if date_key in self.holidays:
            return self.holidays[date_key]
        elif date_key in self.optional_holidays:
            return f"[FACULTATIVO] {self.optional_holidays[date_key]}"
        
        return None
    
    def mark_holidays_in_calendar(self, calendar_dict: Dict) -> Dict:
        """Marca feriados no calendário"""
        marked_calendar = calendar_dict.copy()
        
        for date_key, holiday_name in self.holidays.items():
            if date_key not in marked_calendar:
                marked_calendar[date_key] = {
                    'type': 'holiday',
                    'name': holiday_name,
                    'class': 'holiday'
                }
        
        for date_key, holiday_name in self.optional_holidays.items():
            if date_key not in marked_calendar:
                marked_calendar[date_key] = {
                    'type': 'optional_holiday',
                    'name': holiday_name,
                    'class': 'optional_holiday'
                }
        
        return marked_calendar
    
    def get_holidays_summary(self) -> Dict:
        """Retorna resumo de feriados"""
        return {
            'total_holidays': len(self.holidays),
            'total_optional': len(self.optional_holidays),
            'holidays': self.holidays,
            'optional_holidays': self.optional_holidays
        }


class CalendarWithHolidays:
    """Calendário com marcação automática de feriados"""
    
    def __init__(self, year: int, holidays_file: str = None):
        self.year = year
        self.holiday_manager = HolidayManager(holidays_file)
        self.calendar = {}
    
    def generate_calendar(self) -> Dict:
        """Gera calendário com feriados marcados"""
        from datetime import date, timedelta
        
        calendar = {}
        start_date = date(self.year, 1, 1)
        end_date = date(self.year, 12, 31)
        
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime('%d/%m/%Y')
            
            entry = {
                'date': date_key,
                'day_of_week': current_date.strftime('%A'),
                'is_holiday': False,
                'is_optional_holiday': False,
                'holiday_name': None
            }
            
            # Verificar se é feriado
            if self.holiday_manager.is_holiday(current_date):
                entry['is_holiday'] = True
                entry['holiday_name'] = self.holiday_manager.get_holiday_name(current_date)
            elif self.holiday_manager.is_optional_holiday(current_date):
                entry['is_optional_holiday'] = True
                entry['holiday_name'] = self.holiday_manager.get_holiday_name(current_date)
            
            calendar[date_key] = entry
            current_date += timedelta(days=1)
        
        self.calendar = calendar
        return calendar
    
    def get_non_working_days(self) -> List[str]:
        """Retorna lista de dias não letivos (feriados + fins de semana)"""
        non_working = []
        
        for date_key, entry in self.calendar.items():
            if entry['is_holiday'] or entry['is_optional_holiday']:
                non_working.append(date_key)
            elif entry['day_of_week'] in ['Saturday', 'Sunday']:
                non_working.append(date_key)
        
        return non_working
    
    def get_working_days(self, start_date: str, end_date: str) -> List[str]:
        """Retorna dias úteis em um período"""
        working_days = []
        
        for date_key, entry in self.calendar.items():
            if not entry['is_holiday'] and not entry['is_optional_holiday']:
                if entry['day_of_week'] not in ['Saturday', 'Sunday']:
                    working_days.append(date_key)
        
        return working_days


def main():
    """Teste do módulo"""
    print("=" * 80)
    print("TESTE - GERENCIADOR DE FERIADOS")
    print("=" * 80)
    
    # Criar gerenciador
    holiday_mgr = HolidayManager('Lista_feriados_ponto_facultativo.txt')
    
    # Exibir resumo
    summary = holiday_mgr.get_holidays_summary()
    print(f"\nTotal de feriados: {summary['total_holidays']}")
    print(f"Total de pontos facultativos: {summary['total_optional']}")
    
    print("\nFeriados Nacionais:")
    for date_key, name in sorted(summary['holidays'].items()):
        print(f"  {date_key}: {name}")
    
    print("\nPontos Facultativos:")
    for date_key, name in sorted(summary['optional_holidays'].items()):
        print(f"  {date_key}: {name}")
    
    # Gerar calendário
    print("\n" + "=" * 80)
    print("CALENDÁRIO 2026 COM FERIADOS")
    print("=" * 80)
    
    cal = CalendarWithHolidays(2026, 'Lista_feriados_ponto_facultativo.txt')
    calendar = cal.generate_calendar()
    
    # Exibir alguns dias
    print("\nPrimeiros 10 dias de 2026:")
    for i, (date_key, entry) in enumerate(list(calendar.items())[:10]):
        marker = ""
        if entry['is_holiday']:
            marker = " [FERIADO]"
        elif entry['is_optional_holiday']:
            marker = " [FACULTATIVO]"
        
        print(f"  {date_key} ({entry['day_of_week']}){marker}")
    
    # Dias não úteis
    non_working = cal.get_non_working_days()
    print(f"\nTotal de dias não úteis em 2026: {len(non_working)}")
    print(f"Total de dias úteis em 2026: {366 - len(non_working)}")


if __name__ == "__main__":
    main()
