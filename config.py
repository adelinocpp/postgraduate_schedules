#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração Centralizada do Sistema de Gerenciamento de Horários
"""

import os
from datetime import datetime


class Config:
    """Configurações principais"""
    
    # Informações do Sistema
    SYSTEM_NAME = "Sistema de Gerenciamento de Horários"
    SYSTEM_VERSION = "2.0"
    SYSTEM_AUTHOR = "Equipe de Desenvolvimento"
    
    # Diretórios
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(PROJECT_DIR, 'data')
    OUTPUT_DIR = os.path.join(PROJECT_DIR, 'output')
    LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')
    
    # Criar diretórios se não existirem
    for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]:
        os.makedirs(directory, exist_ok=True)
    
    # Cursos
    COURSES = {
        'criminologia': {
            'name': 'Criminologia',
            'total_hours': 388,
            'disciplines_file': 'DIST_2026-2027_Criminologia.csv',
            'color': '#FF6B6B'
        },
        'gespin': {
            'name': 'Gestão em Segurança Pública e Inteligência Aplicada',
            'total_hours': 388,
            'disciplines_file': 'DIST_2026-2027_GESPIN.csv',
            'color': '#4ECDC4'
        }
    }
    
    # Calendários
    CALENDARS = {
        '2024-2025': {
            'file': 'Calendario_Academico_Criminologia_GESPIN_v6_LImites_OnLine_24_04_2025.ods',
            'status': 'finalizado'
        },
        '2026-2027': {
            'file': 'Calendario_Academico_Criminologia_GESPIN_2026-2027_v2_09_02_2026.ods',
            'status': 'rascunho'
        }
    }
    
    # Horários Padrão
    WEEKLY_SCHEDULE = {
        'days': ['segunda', 'quarta'],
        'slots': [
            {'day': 'segunda', 'time': '19:00-20:40', 'duration': 100},
            {'day': 'segunda', 'time': '21:00-22:40', 'duration': 100},
            {'day': 'quarta', 'time': '19:00-20:40', 'duration': 100},
            {'day': 'quarta', 'time': '21:00-22:40', 'duration': 100},
        ],
        'hours_per_week': 4,
        'semester_1_weeks': 16,
        'semester_2_weeks': 20,
    }
    
    BIWEEKLY_SCHEDULE = {
        'days': ['sexta', 'sábado'],
        'slots': [
            {'day': 'sexta', 'time': '19:00-20:40', 'duration': 100},
            {'day': 'sexta', 'time': '21:00-22:40', 'duration': 100},
            {'day': 'sábado', 'time': '08:00-09:40', 'duration': 100},
            {'day': 'sábado', 'time': '10:00-11:40', 'duration': 100},
            {'day': 'sábado', 'time': '13:00-14:40', 'duration': 100},
            {'day': 'sábado', 'time': '15:00-16:40', 'duration': 100},
        ],
        'hours_per_biweek': 12,
        'semester_1_encounters': 8,
        'semester_2_encounters': 10,
    }
    
    # Feriados
    HOLIDAYS_FILE = 'Lista_feriados_ponto_facultativo.txt'
    
    # Google Drive
    GOOGLE_DRIVE_CONFIG = {
        'enabled': False,  # Ativar após configurar credenciais
        'credentials_file': 'credentials.json',
        'folder_name': 'Horários Pós-Graduação 2026-2027',
        'auto_backup': True,
        'backup_interval_hours': 24
    }
    
    # WhatsApp
    WHATSAPP_CONFIG = {
        'enabled': False,  # Ativar após configurar API
        'api_provider': 'twilio',  # 'twilio' ou 'whatsapp_business'
        'send_schedule_updates': True,
        'send_weekly_schedule': True,
        'send_holiday_alerts': True,
        'schedule_update_day': 'segunda-feira',
        'schedule_update_time': '17:00',
        'contacts_file': 'whatsapp_contacts.json'
    }
    
    # Notificações
    NOTIFICATIONS = {
        'enabled': True,
        'log_file': os.path.join(LOGS_DIR, 'notifications.log'),
        'email_enabled': False,
        'whatsapp_enabled': False,
    }
    
    # Banco de Dados (futuro)
    DATABASE = {
        'type': 'sqlite',  # 'sqlite', 'postgresql', 'mysql'
        'path': os.path.join(DATA_DIR, 'schedules.db'),
        'auto_migrate': True
    }
    
    # Logging
    LOGGING = {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'file': os.path.join(LOGS_DIR, 'system.log'),
        'max_bytes': 10485760,  # 10MB
        'backup_count': 5
    }
    
    # Exportação
    EXPORT_FORMATS = {
        'json': {
            'enabled': True,
            'extension': '.json'
        },
        'ods': {
            'enabled': True,
            'extension': '.ods'
        },
        'pdf': {
            'enabled': True,
            'extension': '.pdf'
        },
        'csv': {
            'enabled': True,
            'extension': '.csv'
        }
    }
    
    # Versionamento
    VERSIONING = {
        'enabled': True,
        'auto_version': True,
        'version_prefix': 'v',
        'max_versions_per_course': 10,
        'keep_history': True
    }


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configurações para testes"""
    DEBUG = True
    TESTING = True
    DATABASE = {
        'type': 'sqlite',
        'path': ':memory:',
        'auto_migrate': True
    }


def get_config(environment: str = 'development') -> Config:
    """
    Retorna configuração baseada no ambiente
    
    Args:
        environment: 'development', 'production' ou 'testing'
    
    Returns:
        Objeto de configuração
    """
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configs.get(environment, DevelopmentConfig)


# Configuração padrão
config = get_config(os.getenv('ENVIRONMENT', 'development'))


if __name__ == "__main__":
    print("=" * 80)
    print("CONFIGURAÇÃO DO SISTEMA")
    print("=" * 80)
    
    print(f"\nSistema: {config.SYSTEM_NAME} v{config.SYSTEM_VERSION}")
    print(f"Ambiente: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Diretório do Projeto: {config.PROJECT_DIR}")
    
    print("\nCursos Configurados:")
    for course_key, course_info in config.COURSES.items():
        print(f"  - {course_info['name']}")
        print(f"    Horas: {course_info['total_hours']}")
    
    print("\nCalendários Disponíveis:")
    for year, cal_info in config.CALENDARS.items():
        print(f"  - {year}: {cal_info['status']}")
    
    print("\nIntegrações:")
    print(f"  - Google Drive: {'Ativado' if config.GOOGLE_DRIVE_CONFIG['enabled'] else 'Desativado'}")
    print(f"  - WhatsApp: {'Ativado' if config.WHATSAPP_CONFIG['enabled'] else 'Desativado'}")
    
    print("\nDiretórios:")
    print(f"  - Dados: {config.DATA_DIR}")
    print(f"  - Saída: {config.OUTPUT_DIR}")
    print(f"  - Logs: {config.LOGS_DIR}")
    
    print("\n✓ Configuração carregada com sucesso")
