#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Gerenciamento de Horários - Módulo Principal
Versão 2.0
"""

import os
import sys
from datetime import datetime
from typing import Dict, List

# Importar módulos do sistema
from schedule_manager import ScheduleManager
from holiday_manager import HolidayManager, CalendarWithHolidays
from google_drive_manager import GoogleDriveManager, VersionManager
from whatsapp_bot import WhatsAppBot, ScheduleNotificationScheduler
from spreadsheet_generator import AdvancedSpreadsheetGenerator
from config import config

# Tentar importar chaves de API
try:
    import api_keys
    API_KEYS_LOADED = True
except ImportError:
    print("[AVISO] Arquivo api_keys.py não encontrado.")
    print("        Copie api_keys.py.template para api_keys.py e configure suas credenciais.")
    API_KEYS_LOADED = False


class ScheduleManagementSystem:
    """Sistema completo de gerenciamento de horários"""
    
    def __init__(self):
        self.schedule_manager = None
        self.holiday_manager = None
        self.drive_manager = None
        self.whatsapp_bot = None
        self.spreadsheet_generator = None
        
        self._initialize_components()
    
    def _initialize_components(self):
        """Inicializa todos os componentes do sistema"""
        print("=" * 80)
        print("INICIALIZANDO SISTEMA DE GERENCIAMENTO DE HORÁRIOS")
        print("=" * 80)
        
        # Holiday Manager
        print("\n[1/5] Inicializando Holiday Manager...")
        self.holiday_manager = HolidayManager('Lista_feriados_ponto_facultativo.txt')
        print("  ✓ Holiday Manager inicializado")
        
        # Google Drive Manager
        print("\n[2/5] Inicializando Google Drive Manager...")
        if API_KEYS_LOADED and hasattr(api_keys, 'GOOGLE_DRIVE_CREDENTIALS_FILE'):
            self.drive_manager = GoogleDriveManager(
                api_keys.GOOGLE_DRIVE_CREDENTIALS_FILE,
                api_keys.GOOGLE_DRIVE_FOLDER_ID
            )
            print("  ✓ Google Drive Manager inicializado")
        else:
            self.drive_manager = GoogleDriveManager()
            print("  ⚠ Google Drive Manager inicializado (modo demo)")
        
        # WhatsApp Bot
        print("\n[3/5] Inicializando WhatsApp Bot...")
        if API_KEYS_LOADED and hasattr(api_keys, 'TWILIO_ACCOUNT_SID'):
            self.whatsapp_bot = WhatsAppBot(
                api_keys.TWILIO_ACCOUNT_SID,
                api_keys.TWILIO_PHONE_NUMBER
            )
            print("  ✓ WhatsApp Bot inicializado")
        else:
            self.whatsapp_bot = WhatsAppBot()
            print("  ⚠ WhatsApp Bot inicializado (modo demo)")
        
        # Spreadsheet Generator
        print("\n[4/5] Inicializando Spreadsheet Generator...")
        self.spreadsheet_generator = AdvancedSpreadsheetGenerator
        print("  ✓ Spreadsheet Generator inicializado")
        
        # Schedule Manager
        print("\n[5/5] Inicializando Schedule Manager...")
        self.schedule_manager = ScheduleManager
        print("  ✓ Schedule Manager inicializado")
        
        print("\n" + "=" * 80)
        print("✓ SISTEMA INICIALIZADO COM SUCESSO")
        print("=" * 80)
    
    def generate_schedules(self, course: str, year: str) -> Dict:
        """
        Gera horários completos para um curso
        
        Args:
            course: Nome do curso (criminologia, gespin)
            year: Ano acadêmico (2026-2027)
        
        Returns:
            Dict com resultados da geração
        """
        print("\n" + "=" * 80)
        print(f"GERANDO HORÁRIOS - {course.upper()} {year}")
        print("=" * 80)
        
        results = {
            'course': course,
            'year': year,
            'timestamp': datetime.now().isoformat(),
            'files': {},
            'notifications': []
        }
        
        # PASSO 1: Gerar horários
        print("\n[PASSO 1/6] Gerando horários...")
        manager = self.schedule_manager(course, year)
        schedule_results = manager.process(
            f'CAL_{year}_Calendario.csv',
            f'DIST_{year}_{course.title()}.csv'
        )
        results['schedule_results'] = schedule_results
        
        # PASSO 2: Gerar planilhas com cores
        print("\n[PASSO 2/6] Gerando planilhas ODS com cores...")
        gen = self.spreadsheet_generator(course, year)
        
        output_dir = config.OUTPUT_DIR
        os.makedirs(output_dir, exist_ok=True)
        
        files = gen.generate_complete_schedule(
            schedule_results,
            self.holiday_manager.get_holidays_summary(),
            output_dir
        )
        results['files'] = files
        
        # PASSO 3: Upload para Google Drive
        print("\n[PASSO 3/6] Fazendo upload para Google Drive...")
        if self.drive_manager and files:
            for file_type, file_path in files.items():
                if os.path.exists(file_path):
                    file_info = self.drive_manager.upload_file(
                        file_path,
                        os.path.basename(file_path),
                        f'{course.title()} {year} - {file_type}'
                    )
                    if file_info:
                        results['files'][f'{file_type}_drive'] = file_info
        
        # PASSO 4: Compartilhar no Drive
        print("\n[PASSO 4/6] Compartilhando arquivos...")
        if API_KEYS_LOADED and hasattr(api_keys, 'GOOGLE_DRIVE_SHARE_WITH'):
            for file_key, file_info in results['files'].items():
                if isinstance(file_info, dict) and 'id' in file_info:
                    self.drive_manager.share_file(
                        file_info['id'],
                        api_keys.GOOGLE_DRIVE_SHARE_WITH,
                        'viewer'
                    )
        
        # PASSO 5: Notificar secretaria via WhatsApp
        print("\n[PASSO 5/6] Notificando secretaria...")
        if API_KEYS_LOADED and hasattr(api_keys, 'NOTIFICATION_CONTACTS'):
            secretaria_phones = [
                c['phone'] for c in api_keys.NOTIFICATION_CONTACTS.get('secretaria', [])
            ]
            
            if secretaria_phones:
                notifications = self.whatsapp_bot.send_schedule_update(
                    course,
                    year,
                    secretaria_phones
                )
                results['notifications'].extend(notifications)
        
        # PASSO 6: Avisar grupo de docentes
        print("\n[PASSO 6/6] Avisando grupo de docentes...")
        if API_KEYS_LOADED and hasattr(api_keys, 'NOTIFICATION_CONTACTS'):
            prof_key = f'professores_{course}'
            prof_phones = [
                c['phone'] for c in api_keys.NOTIFICATION_CONTACTS.get(prof_key, [])
            ]
            
            if prof_phones:
                notifications = self.whatsapp_bot.send_schedule_update(
                    course,
                    year,
                    prof_phones
                )
                results['notifications'].extend(notifications)
        
        print("\n" + "=" * 80)
        print("✓ HORÁRIOS GERADOS COM SUCESSO")
        print("=" * 80)
        
        return results
    
    def update_and_notify(self, course: str, year: str, changes: str):
        """
        Atualiza horários e notifica todos os envolvidos
        
        Args:
            course: Nome do curso
            year: Ano acadêmico
            changes: Descrição das mudanças
        """
        print(f"\n[INFO] Atualizando horários de {course} {year}")
        print(f"[INFO] Mudanças: {changes}")
        
        # Gerar nova versão
        results = self.generate_schedules(course, year)
        
        # Criar versão no Drive
        if self.drive_manager:
            version_mgr = VersionManager(self.drive_manager)
            version = version_mgr.create_schedule_version(
                course,
                year,
                results,
                changes
            )
            print(f"\n[✓] Nova versão criada: v{version['version']}")
        
        return results


def main():
    """Função principal"""
    print("\n" + "=" * 80)
    print("SISTEMA DE GERENCIAMENTO DE HORÁRIOS v2.0")
    print("=" * 80)
    
    # Verificar se api_keys.py existe
    if not API_KEYS_LOADED:
        print("\n[ATENÇÃO] Para usar todas as funcionalidades:")
        print("  1. Copie api_keys.py.template para api_keys.py")
        print("  2. Configure suas credenciais no arquivo api_keys.py")
        print("  3. Execute novamente este script")
        print("\nContinuando em modo demonstração...")
    
    # Criar sistema
    system = ScheduleManagementSystem()
    
    # Menu interativo
    while True:
        print("\n" + "=" * 80)
        print("MENU PRINCIPAL")
        print("=" * 80)
        print("1. Gerar horários Criminologia 2026-2027")
        print("2. Gerar horários GESPIN 2026-2027")
        print("3. Atualizar horário existente")
        print("4. Testar notificações WhatsApp")
        print("5. Verificar feriados")
        print("0. Sair")
        print("=" * 80)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            system.generate_schedules('criminologia', '2026-2027')
        
        elif choice == '2':
            system.generate_schedules('gespin', '2026-2027')
        
        elif choice == '3':
            course = input("Curso (criminologia/gespin): ").strip().lower()
            year = input("Ano (ex: 2026-2027): ").strip()
            changes = input("Descrição das mudanças: ").strip()
            system.update_and_notify(course, year, changes)
        
        elif choice == '4':
            print("\n[INFO] Testando notificações WhatsApp...")
            if system.whatsapp_bot:
                summary = system.whatsapp_bot.get_contacts_summary()
                print(f"Total de contatos: {summary['total_contacts']}")
                print(f"Mensagens enviadas: {summary['total_messages_sent']}")
            else:
                print("[ERRO] WhatsApp Bot não inicializado")
        
        elif choice == '5':
            print("\n[INFO] Feriados e pontos facultativos:")
            if system.holiday_manager:
                summary = system.holiday_manager.get_holidays_summary()
                print(f"Feriados: {summary['total_holidays']}")
                print(f"Pontos facultativos: {summary['total_optional']}")
            else:
                print("[ERRO] Holiday Manager não inicializado")
        
        elif choice == '0':
            print("\n[INFO] Encerrando sistema...")
            break
        
        else:
            print("\n[ERRO] Opção inválida!")


if __name__ == "__main__":
    main()
