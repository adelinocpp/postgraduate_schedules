#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de Planilhas ODS com Cores
Sistema de Gerenciamento de Horários v2.0

Este módulo gera planilhas ODS com formatação e cores idênticas
às planilhas originais dos cursos de Criminologia e GESPIN.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd

try:
    from odf import opendocument, style, table, text
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.style import Style, TableCellProperties, TextProperties
    from odf.table import Table, TableColumn, TableRow, TableCell
    from odf.text import P
    ODF_AVAILABLE = True
except ImportError:
    ODF_AVAILABLE = False
    print("[AVISO] Biblioteca odfpy não encontrada. Instale com: pip install odfpy")


class SpreadsheetColorScheme:
    """
    Esquema de cores baseado nas planilhas originais
    Cores extraídas de CRIMINOLOGIA_2024_2025_SEMANAL_v18_22_04_2025.ods
    """
    
    # Cabeçalhos e estrutura
    HEADER = '#00b0f0'              # Azul claro
    SUBHEADER = '#b3cac7'           # Verde água
    
    # Status de aulas
    PRESENTIAL = '#00b050'          # Verde
    PRESENTIAL_LIGHT = '#afd095'    # Verde claro
    ONLINE = '#acb20c'              # Verde oliva
    ONLINE_LIGHT = '#e2efda'        # Verde muito claro
    
    # Disciplinas (cores rotativas)
    DISCIPLINE_1 = '#8e86ae'        # Roxo/Lilás
    DISCIPLINE_2 = '#b7b3ca'        # Lilás claro
    DISCIPLINE_3 = '#fcd5b4'        # Laranja claro
    DISCIPLINE_4 = '#fce4d6'        # Pêssego
    
    # Alertas e avisos
    HOLIDAY = '#ff6d6d'             # Vermelho
    OPTIONAL_HOLIDAY = '#ffe699'    # Amarelo claro
    WARNING = '#ff972f'             # Laranja
    ATTENTION = '#e6e905'           # Amarelo
    
    # Eventos especiais
    SPECIAL_EVENT = '#ffb3eb'       # Rosa
    OBSERVATION = '#ffbeaf'         # Salmão
    
    # Neutros
    WEEKEND = '#b2b2b2'             # Cinza
    EMPTY = '#dddddd'               # Cinza claro
    DEFAULT = '#ffffff'             # Branco
    
    @classmethod
    def get_discipline_color(cls, discipline_index: int) -> str:
        """Retorna cor para disciplina baseada no índice"""
        colors = [cls.DISCIPLINE_1, cls.DISCIPLINE_2, cls.DISCIPLINE_3, cls.DISCIPLINE_4]
        return colors[discipline_index % len(colors)]
    
    @classmethod
    def get_class_type_color(cls, is_online: bool, is_light: bool = False) -> str:
        """Retorna cor baseada no tipo de aula"""
        if is_online:
            return cls.ONLINE_LIGHT if is_light else cls.ONLINE
        else:
            return cls.PRESENTIAL_LIGHT if is_light else cls.PRESENTIAL


class SpreadsheetGenerator:
    """Gera planilhas ODS com formatação e cores corretas"""
    
    def __init__(self, course: str, year: str, schedule_type: str):
        """
        Inicializa gerador de planilhas
        
        Args:
            course: Nome do curso (criminologia, gespin)
            year: Ano acadêmico (2026-2027)
            schedule_type: Tipo de horário (semanal, quinzenal)
        """
        self.course = course
        self.year = year
        self.schedule_type = schedule_type
        self.schedule_data = {}
        self.calendar_data = {}
        self.colors = SpreadsheetColorScheme()
        
        if not ODF_AVAILABLE:
            raise ImportError("Biblioteca odfpy não disponível. Instale com: pip install odfpy")
        
    def load_schedule(self, schedule_file: str) -> bool:
        """Carrega dados de horário"""
        try:
            with open(schedule_file, 'r', encoding='utf-8') as f:
                self.schedule_data = json.load(f)
            return True
        except Exception as e:
            print(f"[ERRO] Ao carregar horário: {e}")
            return False
    
    def load_calendar(self, calendar_file: str) -> bool:
        """Carrega dados de calendário"""
        try:
            with open(calendar_file, 'r', encoding='utf-8') as f:
                self.calendar_data = json.load(f)
            return True
        except Exception as e:
            print(f"[ERRO] Ao carregar calendário: {e}")
            return False
    
    def _create_style(self, doc: OpenDocumentSpreadsheet, name: str, 
                     bg_color: str, font_weight: str = 'normal',
                     font_size: str = '10pt') -> Style:
        """Cria estilo de célula com cor de fundo"""
        cell_style = Style(name=name, family="table-cell")
        cell_style.addElement(TableCellProperties(backgroundcolor=bg_color))
        cell_style.addElement(TextProperties(fontweight=font_weight, fontsize=font_size))
        doc.automaticstyles.addElement(cell_style)
        return cell_style
    
    def generate_ods(self, output_file: str) -> bool:
        """
        Gera planilha ODS com cores corretas
        
        Args:
            output_file: Caminho do arquivo de saída
        
        Returns:
            bool: True se gerado com sucesso
        """
        try:
            # Criar documento ODS
            doc = OpenDocumentSpreadsheet()
            
            # Criar estilos
            styles = self._create_styles(doc)
            
            # Criar planilha
            sheet = Table(name=f"{self.course.upper()} {self.year} - {self.schedule_type.upper()}")
            
            # Adicionar cabeçalho
            self._add_header(sheet, styles)
            
            # Adicionar dados
            self._add_schedule_data(sheet, styles)
            
            # Adicionar planilha ao documento
            doc.spreadsheet.addElement(sheet)
            
            # Salvar
            doc.save(output_file)
            
            print(f"[✓] Planilha gerada: {output_file}")
            return True
        
        except Exception as e:
            print(f"[✗] Erro ao gerar planilha: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_styles(self, doc: OpenDocumentSpreadsheet) -> Dict[str, Style]:
        """Cria todos os estilos necessários"""
        styles = {}
        
        # Estilos de cabeçalho
        styles['header'] = self._create_style(doc, 'header', self.colors.HEADER, 'bold', '12pt')
        styles['subheader'] = self._create_style(doc, 'subheader', self.colors.SUBHEADER, 'bold', '11pt')
        
        # Estilos de aulas
        styles['presential'] = self._create_style(doc, 'presential', self.colors.PRESENTIAL)
        styles['presential_light'] = self._create_style(doc, 'presential_light', self.colors.PRESENTIAL_LIGHT)
        styles['online'] = self._create_style(doc, 'online', self.colors.ONLINE)
        styles['online_light'] = self._create_style(doc, 'online_light', self.colors.ONLINE_LIGHT)
        
        # Estilos de disciplinas
        for i in range(4):
            color = self.colors.get_discipline_color(i)
            styles[f'discipline_{i}'] = self._create_style(doc, f'discipline_{i}', color)
        
        # Estilos de alertas
        styles['holiday'] = self._create_style(doc, 'holiday', self.colors.HOLIDAY, 'bold')
        styles['optional_holiday'] = self._create_style(doc, 'optional_holiday', self.colors.OPTIONAL_HOLIDAY)
        styles['warning'] = self._create_style(doc, 'warning', self.colors.WARNING)
        styles['attention'] = self._create_style(doc, 'attention', self.colors.ATTENTION)
        
        # Estilos neutros
        styles['weekend'] = self._create_style(doc, 'weekend', self.colors.WEEKEND)
        styles['empty'] = self._create_style(doc, 'empty', self.colors.EMPTY)
        styles['default'] = self._create_style(doc, 'default', self.colors.DEFAULT)
        
        return styles
    
    def _add_header(self, sheet: Table, styles: Dict[str, Style]):
        """Adiciona cabeçalho à planilha"""
        # Primeira linha - Título
        row = TableRow()
        cell = TableCell(stylename=styles['header'], valuetype="string")
        cell.addElement(P(text=f"HORÁRIO {self.course.upper()} {self.year} - TURMA {self.schedule_type.upper()}"))
        row.addElement(cell)
        sheet.addElement(row)
        
        # Segunda linha - Cabeçalhos de colunas
        row = TableRow()
        if self.schedule_type == 'semanal':
            headers = ['Data', 'Dia', 'Segunda 19:00-20:40', 'Segunda 21:00-22:40',
                      'Quarta 19:00-20:40', 'Quarta 21:00-22:40', 'Observações']
        else:  # quinzenal
            headers = ['Data', 'Dia', 'Sexta 19:00-20:40', 'Sexta 21:00-22:40',
                      'Sábado 08:00-09:40', 'Sábado 10:00-11:40',
                      'Sábado 13:00-14:40', 'Sábado 15:00-16:40', 'Observações']
        
        for header in headers:
            cell = TableCell(stylename=styles['subheader'], valuetype="string")
            cell.addElement(P(text=header))
            row.addElement(cell)
        sheet.addElement(row)
    
    def _add_schedule_data(self, sheet: Table, styles: Dict[str, Style]):
        """Adiciona dados de horário à planilha"""
        # Dados de exemplo (em produção, usar dados reais do schedule_data)
        start_date = datetime(2026, 3, 1)
        
        for week in range(50):  # 50 semanas
            date = start_date + timedelta(weeks=week)
            
            row = TableRow()
            
            # Data
            cell = TableCell(stylename=styles['default'], valuetype="string")
            cell.addElement(P(text=date.strftime('%d/%m/%Y')))
            row.addElement(cell)
            
            # Dia da semana
            cell = TableCell(stylename=styles['default'], valuetype="string")
            cell.addElement(P(text=date.strftime('%A')))
            row.addElement(cell)
            
            # Slots de horário (vazio por enquanto)
            num_slots = 4 if self.schedule_type == 'semanal' else 6
            for i in range(num_slots):
                cell = TableCell(stylename=styles['empty'], valuetype="string")
                cell.addElement(P(text=''))
                row.addElement(cell)
            
            # Observações
            cell = TableCell(stylename=styles['default'], valuetype="string")
            cell.addElement(P(text=''))
            row.addElement(cell)
            
            sheet.addElement(row)
    
    def generate_pdf(self, ods_file: str, pdf_file: str) -> bool:
        """
        Gera PDF a partir da planilha ODS usando LibreOffice
        
        Args:
            ods_file: Arquivo ODS de entrada
            pdf_file: Arquivo PDF de saída
        
        Returns:
            bool: True se gerado com sucesso
        """
        try:
            import subprocess
            
            output_dir = os.path.dirname(pdf_file) or '.'
            
            cmd = [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', output_dir,
                ods_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print(f"[✓] PDF gerado: {pdf_file}")
                return True
            else:
                print(f"[✗] Erro ao gerar PDF: {result.stderr}")
                return False
        
        except Exception as e:
            print(f"[✗] Erro ao gerar PDF: {e}")
            return False


class AdvancedSpreadsheetGenerator:
    """Gerador avançado com suporte completo a cores ODS"""
    
    def __init__(self, course: str, year: str):
        self.course = course
        self.year = year
        
    def generate_complete_schedule(self, 
                                   schedule_data: Dict,
                                   calendar_data: Dict,
                                   output_dir: str) -> Dict[str, str]:
        """
        Gera planilhas completas para todas as turmas
        
        Args:
            schedule_data: Dados dos horários
            calendar_data: Dados do calendário
            output_dir: Diretório de saída
        
        Returns:
            Dict com caminhos dos arquivos gerados
        """
        files = {}
        
        # Criar diretório se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Gerar planilha semanal
        print(f"\n[INFO] Gerando planilha semanal para {self.course}...")
        weekly_gen = SpreadsheetGenerator(self.course, self.year, 'semanal')
        weekly_file = f"{output_dir}/{self.course}_{self.year}_semanal.ods"
        
        if weekly_gen.generate_ods(weekly_file):
            files['weekly_ods'] = weekly_file
            
            # Gerar PDF correspondente
            weekly_pdf = weekly_file.replace('.ods', '.pdf')
            if weekly_gen.generate_pdf(weekly_file, weekly_pdf):
                files['weekly_pdf'] = weekly_pdf
        
        # Gerar planilha quinzenal
        print(f"\n[INFO] Gerando planilha quinzenal para {self.course}...")
        biweekly_gen = SpreadsheetGenerator(self.course, self.year, 'quinzenal')
        biweekly_file = f"{output_dir}/{self.course}_{self.year}_quinzenal.ods"
        
        if biweekly_gen.generate_ods(biweekly_file):
            files['biweekly_ods'] = biweekly_file
            
            # Gerar PDF correspondente
            biweekly_pdf = biweekly_file.replace('.ods', '.pdf')
            if biweekly_gen.generate_pdf(biweekly_file, biweekly_pdf):
                files['biweekly_pdf'] = biweekly_pdf
        
        return files


def main():
    """Teste do gerador"""
    print("=" * 80)
    print("TESTE - GERADOR DE PLANILHAS COM CORES CORRETAS")
    print("=" * 80)
    
    if not ODF_AVAILABLE:
        print("\n[ERRO] Biblioteca odfpy não instalada!")
        print("Instale com: pip install odfpy")
        return
    
    # Criar gerador
    gen = SpreadsheetGenerator('criminologia', '2026-2027', 'semanal')
    
    # Gerar planilha
    output_file = 'test_schedule_with_colors.ods'
    if gen.generate_ods(output_file):
        print(f"\n✓ Planilha gerada com sucesso: {output_file}")
        print(f"✓ Cores aplicadas conforme planilhas originais")
    else:
        print(f"\n✗ Falha ao gerar planilha")
    
    # Testar gerador avançado
    print("\n" + "=" * 80)
    print("TESTE - GERADOR AVANÇADO")
    print("=" * 80)
    
    adv_gen = AdvancedSpreadsheetGenerator('criminologia', '2026-2027')
    
    schedule_data = {'course': 'criminologia', 'year': '2026-2027'}
    calendar_data = {'year': 2026}
    
    files = adv_gen.generate_complete_schedule(
        schedule_data,
        calendar_data,
        './output'
    )
    
    print("\nArquivos gerados:")
    for key, path in files.items():
        print(f"  - {key}: {path}")
    
    print("\n" + "=" * 80)
    print("CORES UTILIZADAS (baseadas nas planilhas originais):")
    print("=" * 80)
    print(f"  Cabeçalho: {SpreadsheetColorScheme.HEADER}")
    print(f"  Presencial: {SpreadsheetColorScheme.PRESENTIAL}")
    print(f"  Online: {SpreadsheetColorScheme.ONLINE}")
    print(f"  Feriado: {SpreadsheetColorScheme.HOLIDAY}")
    print(f"  Ponto Facultativo: {SpreadsheetColorScheme.OPTIONAL_HOLIDAY}")
    print(f"  Fim de semana: {SpreadsheetColorScheme.WEEKEND}")


if __name__ == "__main__":
    main()
