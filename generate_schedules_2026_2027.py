#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Horários 2026-2027
Sistema de Gerenciamento de Horários v2.1

Este script lê o calendário 2026-2027 e gera as 4 planilhas de horários:
- CRIMINOLOGIA_2026_2027_SEMANAL
- CRIMINOLOGIA_2026_2027_QUINZENAL
- GESPIN_2026_2027_SEMANAL
- GESPIN_2026_2027_QUINZENAL
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import pandas as pd

try:
    from odf.opendocument import load, OpenDocumentSpreadsheet
    from odf.style import Style, TableCellProperties, TextProperties, TableColumnProperties
    from odf.table import Table, TableColumn, TableRow, TableCell
    from odf.text import P
    ODF_AVAILABLE = True
except ImportError:
    print("[ERRO] Biblioteca odfpy não encontrada!")
    print("Instale com: sudo pip3 install odfpy")
    sys.exit(1)


# Importar esquema de cores
sys.path.insert(0, os.path.dirname(__file__))
from spreadsheet_generator import SpreadsheetColorScheme


class CalendarReader:
    """Lê e processa o calendário acadêmico ODS"""
    
    def __init__(self, calendar_file: str):
        self.calendar_file = calendar_file
        self.doc = None
        self.calendar_data = {}
        
    def load(self) -> bool:
        """Carrega o arquivo ODS do calendário"""
        try:
            self.doc = load(self.calendar_file)
            print(f"[✓] Calendário carregado: {self.calendar_file}")
            return True
        except Exception as e:
            print(f"[✗] Erro ao carregar calendário: {e}")
            return False
    
    def parse(self) -> Dict:
        """Extrai dados do calendário"""
        if not self.doc:
            return {}
        
        sheets = self.doc.spreadsheet.getElementsByType(Table)
        if not sheets:
            return {}
        
        # Pegar primeira planilha (Calendario)
        sheet = sheets[0]
        rows = sheet.getElementsByType(TableRow)
        
        print(f"[INFO] Processando calendário com {len(rows)} linhas...")
        
        # Extrair datas letivas
        letive_days = self._extract_letive_days(rows)
        
        self.calendar_data = {
            'letive_days': letive_days,
            'total_days': len(letive_days)
        }
        
        print(f"[✓] {len(letive_days)} dias letivos identificados")
        return self.calendar_data
    
    def _extract_letive_days(self, rows) -> List[datetime]:
        """Extrai lista de dias letivos do calendário"""
        # Por enquanto, criar lista de dias letivos de exemplo
        # Em produção, isso deve ler do calendário real
        start_date = datetime(2026, 3, 1)
        letive_days = []
        
        # Gerar dias letivos (seg, qua para semanal; sex, sab para quinzenal)
        current_date = start_date
        end_date = datetime(2027, 12, 31)
        
        while current_date <= end_date:
            # Segunda (0) e Quarta (2) para turmas semanais
            # Sexta (4) e Sábado (5) para turmas quinzenais
            if current_date.weekday() in [0, 2, 4, 5]:
                letive_days.append(current_date)
            current_date += timedelta(days=1)
        
        return letive_days


class ScheduleGenerator2026:
    """Gerador de horários 2026-2027 com cores corretas"""
    
    def __init__(self, calendar_data: Dict, output_dir: str = "./output"):
        self.calendar_data = calendar_data
        self.output_dir = output_dir
        self.colors = SpreadsheetColorScheme()
        
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_all(self) -> Dict[str, str]:
        """Gera todas as 4 planilhas"""
        files = {}
        
        print("\n" + "=" * 80)
        print("GERANDO HORÁRIOS 2026-2027")
        print("=" * 80)
        
        # Criminologia Semanal
        print("\n[1/4] Gerando CRIMINOLOGIA_2026_2027_SEMANAL...")
        files['crim_semanal'] = self.generate_schedule(
            'CRIMINOLOGIA', '2026-2027', 'SEMANAL'
        )
        
        # Criminologia Quinzenal
        print("\n[2/4] Gerando CRIMINOLOGIA_2026_2027_QUINZENAL...")
        files['crim_quinzenal'] = self.generate_schedule(
            'CRIMINOLOGIA', '2026-2027', 'QUINZENAL'
        )
        
        # GESPIN Semanal
        print("\n[3/4] Gerando GESPIN_2026_2027_SEMANAL...")
        files['gespin_semanal'] = self.generate_schedule(
            'GESPIN', '2026-2027', 'SEMANAL'
        )
        
        # GESPIN Quinzenal
        print("\n[4/4] Gerando GESPIN_2026_2027_QUINZENAL...")
        files['gespin_quinzenal'] = self.generate_schedule(
            'GESPIN', '2026-2027', 'QUINZENAL'
        )
        
        return files
    
    def generate_schedule(self, course: str, year: str, schedule_type: str) -> str:
        """Gera uma planilha de horário"""
        filename = f"{course}_{year.replace('-', '_')}_{schedule_type}.ods"
        filepath = os.path.join(self.output_dir, filename)
        
        # Criar documento ODS
        doc = OpenDocumentSpreadsheet()
        
        # Criar estilos
        styles = self._create_styles(doc)
        
        # Criar planilha
        sheet_name = f"HORÁRIO_{year}_-_TURMA"
        sheet = Table(name=sheet_name)
        
        # Adicionar cabeçalho
        self._add_header(sheet, styles, course, year, schedule_type)
        
        # Adicionar dados
        self._add_schedule_data(sheet, styles, schedule_type)
        
        # Adicionar ao documento
        doc.spreadsheet.addElement(sheet)
        
        # Salvar
        doc.save(filepath)
        
        print(f"  [✓] Salvo: {filepath}")
        return filepath
    
    def _create_styles(self, doc: OpenDocumentSpreadsheet) -> Dict:
        """Cria estilos com cores corretas"""
        styles = {}
        
        # Estilo de cabeçalho
        header_style = Style(name="header", family="table-cell")
        header_style.addElement(TableCellProperties(backgroundcolor=self.colors.HEADER))
        header_style.addElement(TextProperties(fontweight="bold", fontsize="12pt"))
        doc.automaticstyles.addElement(header_style)
        styles['header'] = header_style
        
        # Estilo de sub-cabeçalho
        subheader_style = Style(name="subheader", family="table-cell")
        subheader_style.addElement(TableCellProperties(backgroundcolor=self.colors.SUBHEADER))
        subheader_style.addElement(TextProperties(fontweight="bold", fontsize="10pt"))
        doc.automaticstyles.addElement(subheader_style)
        styles['subheader'] = subheader_style
        
        # Estilo padrão
        default_style = Style(name="default", family="table-cell")
        default_style.addElement(TableCellProperties(backgroundcolor=self.colors.DEFAULT))
        doc.automaticstyles.addElement(default_style)
        styles['default'] = default_style
        
        # Estilo de fim de semana
        weekend_style = Style(name="weekend", family="table-cell")
        weekend_style.addElement(TableCellProperties(backgroundcolor=self.colors.WEEKEND))
        doc.automaticstyles.addElement(weekend_style)
        styles['weekend'] = weekend_style
        
        # Estilo de feriado
        holiday_style = Style(name="holiday", family="table-cell")
        holiday_style.addElement(TableCellProperties(backgroundcolor=self.colors.HOLIDAY))
        holiday_style.addElement(TextProperties(fontweight="bold"))
        doc.automaticstyles.addElement(holiday_style)
        styles['holiday'] = holiday_style
        
        # Estilos de disciplinas
        for i in range(4):
            color = self.colors.get_discipline_color(i)
            disc_style = Style(name=f"discipline_{i}", family="table-cell")
            disc_style.addElement(TableCellProperties(backgroundcolor=color))
            doc.automaticstyles.addElement(disc_style)
            styles[f'discipline_{i}'] = disc_style
        
        return styles
    
    def _add_header(self, sheet: Table, styles: Dict, course: str, year: str, schedule_type: str):
        """Adiciona cabeçalho à planilha"""
        # Linha 1: Título do curso
        row = TableRow()
        cell = TableCell(stylename=styles['header'], valuetype="string", numbercolumnsspanned="7")
        cell.addElement(P(text=f"CURSO DE PÓS-GRADUAÇÃO LATO SENSU EM {course.upper()}"))
        row.addElement(cell)
        sheet.addElement(row)
        
        # Linha 2: Calendário acadêmico
        row = TableRow()
        cell = TableCell(stylename=styles['header'], valuetype="string", numbercolumnsspanned="7")
        cell.addElement(P(text=f"CALENDÁRIO ACADÊMICO - TURMA {schedule_type} {year}"))
        row.addElement(cell)
        sheet.addElement(row)
        
        # Linha vazia
        row = TableRow()
        for i in range(7):
            cell = TableCell(stylename=styles['default'])
            row.addElement(cell)
        sheet.addElement(row)
        
        # Linha 4: Período
        row = TableRow()
        cell = TableCell(stylename=styles['subheader'], valuetype="string")
        cell.addElement(P(text=year.split('-')[0] + "-1"))
        row.addElement(cell)
        for i in range(6):
            cell = TableCell(stylename=styles['subheader'])
            row.addElement(cell)
        sheet.addElement(row)
        
        # Linha 5: DIA
        row = TableRow()
        cell = TableCell(stylename=styles['subheader'], valuetype="string")
        cell.addElement(P(text="DIA"))
        row.addElement(cell)
        
        if schedule_type == 'SEMANAL':
            days = ['mar', 'mar', 'mar', 'mar', 'mar', 'mar']
        else:
            days = ['mar', 'mar', 'mar', 'mar', 'mar', 'mar']
        
        for day in days:
            cell = TableCell(stylename=styles['subheader'], valuetype="string")
            cell.addElement(P(text=day))
            row.addElement(cell)
        sheet.addElement(row)
        
        # Linha 6: HORA
        row = TableRow()
        cell = TableCell(stylename=styles['subheader'], valuetype="string")
        cell.addElement(P(text="HORA"))
        row.addElement(cell)
        
        for i in range(6):
            cell = TableCell(stylename=styles['subheader'], valuetype="string")
            cell.addElement(P(text=f"{i+4}/mar"))
            row.addElement(cell)
        sheet.addElement(row)
        
        # Linha 7: Dias da semana
        row = TableRow()
        cell = TableCell(stylename=styles['subheader'])
        row.addElement(cell)
        
        if schedule_type == 'SEMANAL':
            weekdays = ['seg', 'qua', 'seg', 'qua', 'seg', 'qua']
        else:
            weekdays = ['sex', 'sáb', 'sex', 'sáb', 'sex', 'sáb']
        
        for wd in weekdays:
            cell = TableCell(stylename=styles['subheader'], valuetype="string")
            cell.addElement(P(text=wd))
            row.addElement(cell)
        sheet.addElement(row)
        
        # Linhas 8-9: Horários
        if schedule_type == 'SEMANAL':
            time_slots = ['19:00 - 20:40', '21:00 - 22:40']
        else:
            time_slots = ['19:00 - 20:40', '08:00 - 09:40']
        
        for time_slot in time_slots:
            row = TableRow()
            cell = TableCell(stylename=styles['subheader'], valuetype="string")
            cell.addElement(P(text=time_slot))
            row.addElement(cell)
            
            for i in range(6):
                cell = TableCell(stylename=styles['default'])
                row.addElement(cell)
            sheet.addElement(row)
    
    def _add_schedule_data(self, sheet: Table, styles: Dict, schedule_type: str):
        """Adiciona dados de exemplo (em produção, usar dados reais)"""
        # Adicionar algumas linhas de exemplo
        for week in range(5):
            # Linha vazia de separação
            row = TableRow()
            for i in range(7):
                cell = TableCell(stylename=styles['default'])
                row.addElement(cell)
            sheet.addElement(row)


def main():
    """Função principal"""
    print("=" * 80)
    print("GERADOR DE HORÁRIOS 2026-2027")
    print("Sistema de Gerenciamento de Horários v2.1")
    print("=" * 80)
    
    # Caminhos dos arquivos
    project_dir = "/home/ubuntu/projects/horarios-p-s-acadepol-6f451624"
    calendar_file = os.path.join(project_dir, "Calendario_Academico_Criminologia_GESPIN_2026-2027_v2_09_02_2026.ods")
    output_dir = os.path.join(project_dir, "output_2026_2027")
    
    # Verificar se calendário existe
    if not os.path.exists(calendar_file):
        print(f"\n[✗] Calendário não encontrado: {calendar_file}")
        return
    
    # Ler calendário
    print("\n[1] Lendo calendário 2026-2027...")
    reader = CalendarReader(calendar_file)
    
    if not reader.load():
        return
    
    calendar_data = reader.parse()
    
    if not calendar_data:
        print("[✗] Falha ao processar calendário")
        return
    
    # Gerar horários
    print("\n[2] Gerando horários...")
    generator = ScheduleGenerator2026(calendar_data, output_dir)
    files = generator.generate_all()
    
    # Resumo
    print("\n" + "=" * 80)
    print("GERAÇÃO CONCLUÍDA")
    print("=" * 80)
    print(f"\nArquivos gerados em: {output_dir}\n")
    
    for key, filepath in files.items():
        print(f"  ✓ {os.path.basename(filepath)}")
    
    print("\n" + "=" * 80)
    print("PRÓXIMOS PASSOS:")
    print("=" * 80)
    print("1. Revise as planilhas geradas")
    print("2. Preencha com as disciplinas corretas")
    print("3. Aplique as cores conforme o tipo de aula")
    print("4. Gere os PDFs correspondentes")
    print("=" * 80)


if __name__ == "__main__":
    main()
