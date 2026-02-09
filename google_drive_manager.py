#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Integração com Google Drive
Para versionamento e compartilhamento de horários
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


class GoogleDriveManager:
    """Gerencia integração com Google Drive"""
    
    def __init__(self, credentials_file: str = None, folder_id: str = None):
        """
        Inicializa gerenciador do Google Drive
        
        Args:
            credentials_file: Caminho para arquivo de credenciais JSON
            folder_id: ID da pasta no Google Drive para armazenar arquivos
        """
        self.credentials_file = credentials_file
        self.folder_id = folder_id
        self.service = None
        self.version_history = []
        
        # Nota: Em produção, usar google-auth-oauthlib
        # Para agora, criar estrutura de exemplo
        self._initialize_mock_service()
    
    def _initialize_mock_service(self):
        """Inicializa serviço mock (para demonstração)"""
        print("[INFO] Google Drive Manager inicializado (modo demo)")
        print("[INFO] Para usar em produção, configure credenciais OAuth 2.0")
    
    def authenticate(self, credentials_path: str) -> bool:
        """
        Autentica com Google Drive
        
        Requer:
        - pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
        
        Args:
            credentials_path: Caminho para arquivo credentials.json
        
        Returns:
            bool: True se autenticado com sucesso
        """
        try:
            # from google.auth.transport.requests import Request
            # from google.oauth2.service_account import Credentials
            # from googleapiclient.discovery import build
            
            # credentials = Credentials.from_service_account_file(
            #     credentials_path,
            #     scopes=['https://www.googleapis.com/auth/drive']
            # )
            # self.service = build('drive', 'v3', credentials=credentials)
            
            print(f"[INFO] Autenticação com Google Drive configurada")
            print(f"[INFO] Credenciais: {credentials_path}")
            return True
        except Exception as e:
            print(f"[ERRO] Falha na autenticação: {e}")
            return False
    
    def upload_file(self, file_path: str, file_name: str = None, 
                   description: str = None) -> Optional[Dict]:
        """
        Faz upload de arquivo para Google Drive
        
        Args:
            file_path: Caminho local do arquivo
            file_name: Nome do arquivo no Drive (opcional)
            description: Descrição do arquivo
        
        Returns:
            Dict com informações do arquivo ou None se falhar
        """
        try:
            if not file_name:
                file_name = file_path.split('/')[-1]
            
            # Estrutura de resposta simulada
            file_info = {
                'id': f'drive_id_{datetime.now().timestamp()}',
                'name': file_name,
                'path': file_path,
                'uploaded_at': datetime.now().isoformat(),
                'description': description,
                'size': 0,  # Seria obtido do arquivo real
                'mime_type': self._get_mime_type(file_path),
                'web_view_link': f'https://drive.google.com/file/d/drive_id/view'
            }
            
            # Adicionar ao histórico de versões
            self.version_history.append(file_info)
            
            print(f"[✓] Arquivo enviado: {file_name}")
            return file_info
        
        except Exception as e:
            print(f"[✗] Erro ao fazer upload: {e}")
            return None
    
    def create_version(self, file_path: str, version_number: int, 
                      notes: str = None) -> Optional[Dict]:
        """
        Cria nova versão de arquivo
        
        Args:
            file_path: Caminho do arquivo
            version_number: Número da versão
            notes: Notas sobre a versão
        
        Returns:
            Dict com informações da versão
        """
        try:
            version_info = {
                'version': version_number,
                'file_path': file_path,
                'created_at': datetime.now().isoformat(),
                'notes': notes,
                'file_name': file_path.split('/')[-1],
                'drive_id': f'v{version_number}_{datetime.now().timestamp()}'
            }
            
            self.version_history.append(version_info)
            
            print(f"[✓] Versão {version_number} criada")
            return version_info
        
        except Exception as e:
            print(f"[✗] Erro ao criar versão: {e}")
            return None
    
    def share_file(self, file_id: str, email_list: List[str], 
                  role: str = 'viewer') -> bool:
        """
        Compartilha arquivo com usuários
        
        Args:
            file_id: ID do arquivo no Drive
            email_list: Lista de emails para compartilhar
            role: 'viewer', 'commenter' ou 'writer'
        
        Returns:
            bool: True se compartilhado com sucesso
        """
        try:
            for email in email_list:
                print(f"[✓] Compartilhado com: {email} ({role})")
            
            return True
        
        except Exception as e:
            print(f"[✗] Erro ao compartilhar: {e}")
            return False
    
    def create_shared_folder(self, folder_name: str, 
                            shared_with: List[str] = None) -> Optional[Dict]:
        """
        Cria pasta compartilhada no Drive
        
        Args:
            folder_name: Nome da pasta
            shared_with: Lista de emails para compartilhar
        
        Returns:
            Dict com informações da pasta
        """
        try:
            folder_info = {
                'id': f'folder_{datetime.now().timestamp()}',
                'name': folder_name,
                'created_at': datetime.now().isoformat(),
                'shared_with': shared_with or [],
                'web_link': f'https://drive.google.com/drive/folders/folder_id'
            }
            
            print(f"[✓] Pasta criada: {folder_name}")
            
            if shared_with:
                for email in shared_with:
                    print(f"  └─ Compartilhado com: {email}")
            
            return folder_info
        
        except Exception as e:
            print(f"[✗] Erro ao criar pasta: {e}")
            return None
    
    def get_version_history(self) -> List[Dict]:
        """Retorna histórico de versões"""
        return self.version_history
    
    def _get_mime_type(self, file_path: str) -> str:
        """Determina tipo MIME do arquivo"""
        if file_path.endswith('.json'):
            return 'application/json'
        elif file_path.endswith('.pdf'):
            return 'application/pdf'
        elif file_path.endswith('.ods'):
            return 'application/vnd.oasis.opendocument.spreadsheet'
        elif file_path.endswith('.xlsx'):
            return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        else:
            return 'application/octet-stream'


class VersionManager:
    """Gerencia versões de horários"""
    
    def __init__(self, drive_manager: GoogleDriveManager):
        self.drive_manager = drive_manager
        self.versions = {}
    
    def create_schedule_version(self, course: str, year: str, 
                               schedule_data: Dict, notes: str = None) -> Dict:
        """
        Cria versão de horário
        
        Args:
            course: Nome do curso
            year: Ano acadêmico
            schedule_data: Dados do horário
            notes: Notas da versão
        
        Returns:
            Dict com informações da versão
        """
        version_key = f"{course}_{year}"
        
        if version_key not in self.versions:
            self.versions[version_key] = []
        
        version_number = len(self.versions[version_key]) + 1
        
        version_info = {
            'course': course,
            'year': year,
            'version': version_number,
            'created_at': datetime.now().isoformat(),
            'notes': notes,
            'data': schedule_data,
            'file_name': f'{course}_{year}_v{version_number}.json'
        }
        
        self.versions[version_key].append(version_info)
        
        return version_info
    
    def get_latest_version(self, course: str, year: str) -> Optional[Dict]:
        """Retorna última versão de um horário"""
        version_key = f"{course}_{year}"
        
        if version_key in self.versions and self.versions[version_key]:
            return self.versions[version_key][-1]
        
        return None
    
    def compare_versions(self, course: str, year: str, 
                        v1: int, v2: int) -> Dict:
        """
        Compara duas versões de horário
        
        Args:
            course: Nome do curso
            year: Ano acadêmico
            v1: Número da primeira versão
            v2: Número da segunda versão
        
        Returns:
            Dict com diferenças entre versões
        """
        version_key = f"{course}_{year}"
        
        if version_key not in self.versions:
            return {'error': 'Nenhuma versão encontrada'}
        
        versions = self.versions[version_key]
        
        # Encontrar versões
        ver1 = next((v for v in versions if v['version'] == v1), None)
        ver2 = next((v for v in versions if v['version'] == v2), None)
        
        if not ver1 or not ver2:
            return {'error': 'Versão não encontrada'}
        
        return {
            'course': course,
            'year': year,
            'version_1': v1,
            'version_2': v2,
            'created_at_v1': ver1['created_at'],
            'created_at_v2': ver2['created_at'],
            'notes_v1': ver1['notes'],
            'notes_v2': ver2['notes'],
            'comparison': 'Comparação de versões'
        }


def main():
    """Teste do módulo"""
    print("=" * 80)
    print("TESTE - GERENCIADOR GOOGLE DRIVE")
    print("=" * 80)
    
    # Criar gerenciador
    drive_mgr = GoogleDriveManager()
    
    # Simular upload de arquivo
    print("\n[1] Fazendo upload de arquivo...")
    file_info = drive_mgr.upload_file(
        'schedule_results_criminologia_2026_2027.json',
        'Horário_Criminologia_2026-2027_v1.json',
        'Versão inicial do horário de Criminologia'
    )
    
    # Criar pasta compartilhada
    print("\n[2] Criando pasta compartilhada...")
    folder_info = drive_mgr.create_shared_folder(
        'Horários Pós-Graduação 2026-2027',
        ['professor1@example.com', 'professor2@example.com', 'secretaria@example.com']
    )
    
    # Gerenciar versões
    print("\n[3] Gerenciando versões...")
    version_mgr = VersionManager(drive_mgr)
    
    schedule_data = {
        'course': 'criminologia',
        'year': '2026-2027',
        'total_hours': 388,
        'semesters': 2
    }
    
    v1 = version_mgr.create_schedule_version(
        'criminologia',
        '2026-2027',
        schedule_data,
        'Versão inicial com calendário 2026-2027'
    )
    
    print(f"\n✓ Versão criada: v{v1['version']}")
    print(f"  Arquivo: {v1['file_name']}")
    print(f"  Data: {v1['created_at']}")
    
    # Histórico de versões
    print("\n[4] Histórico de versões:")
    history = drive_mgr.get_version_history()
    for item in history:
        if 'version' in item:
            print(f"  - Versão {item['version']}: {item['created_at']}")


if __name__ == "__main__":
    main()
