#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot WhatsApp para Notificações de Horários
Integrado ao Sistema de Gerenciamento de Horários
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class MessageType(Enum):
    """Tipos de mensagens"""
    SCHEDULE_UPDATE = "schedule_update"
    WEEKLY_SCHEDULE = "weekly_schedule"
    HOLIDAY_ALERT = "holiday_alert"
    GENERAL_INFO = "general_info"


class WhatsAppBot:
    """Bot para enviar notificações via WhatsApp"""
    
    def __init__(self, api_key: str = None, phone_number: str = None):
        """
        Inicializa bot WhatsApp
        
        Args:
            api_key: Chave da API (Twilio, WhatsApp Business API, etc)
            phone_number: Número de telefone do bot
        """
        self.api_key = api_key
        self.phone_number = phone_number
        self.message_queue = []
        self.sent_messages = []
        self.contacts = {}
        
        print("[INFO] WhatsApp Bot inicializado")
        print("[INFO] Para usar em produção, configure:")
        print("       - pip install twilio")
        print("       - Credenciais da Twilio ou WhatsApp Business API")
    
    def add_contact(self, name: str, phone: str, role: str = None) -> bool:
        """
        Adiciona contato
        
        Args:
            name: Nome do contato
            phone: Número de telefone (com código do país)
            role: Função (professor, secretaria, etc)
        
        Returns:
            bool: True se adicionado com sucesso
        """
        try:
            self.contacts[phone] = {
                'name': name,
                'phone': phone,
                'role': role,
                'added_at': datetime.now().isoformat()
            }
            print(f"[✓] Contato adicionado: {name} ({phone})")
            return True
        except Exception as e:
            print(f"[✗] Erro ao adicionar contato: {e}")
            return False
    
    def add_group(self, group_name: str, members: List[Dict]) -> bool:
        """
        Cria grupo de contatos
        
        Args:
            group_name: Nome do grupo
            members: Lista de dicts com 'name' e 'phone'
        
        Returns:
            bool: True se criado com sucesso
        """
        try:
            for member in members:
                self.add_contact(member['name'], member['phone'], 'group_member')
            
            print(f"[✓] Grupo criado: {group_name} ({len(members)} membros)")
            return True
        except Exception as e:
            print(f"[✗] Erro ao criar grupo: {e}")
            return False
    
    def send_message(self, phone: str, message: str, 
                    message_type: MessageType = MessageType.GENERAL_INFO) -> Optional[Dict]:
        """
        Envia mensagem para contato
        
        Args:
            phone: Número de telefone
            message: Conteúdo da mensagem
            message_type: Tipo de mensagem
        
        Returns:
            Dict com informações do envio ou None se falhar
        """
        try:
            message_info = {
                'id': f'msg_{datetime.now().timestamp()}',
                'to': phone,
                'message': message,
                'type': message_type.value,
                'sent_at': datetime.now().isoformat(),
                'status': 'sent'
            }
            
            self.sent_messages.append(message_info)
            
            print(f"[✓] Mensagem enviada para {phone}")
            return message_info
        
        except Exception as e:
            print(f"[✗] Erro ao enviar mensagem: {e}")
            return None
    
    def send_schedule_update(self, course: str, year: str, 
                            recipients: List[str] = None) -> List[Dict]:
        """
        Envia atualização de horário
        
        Args:
            course: Nome do curso
            year: Ano acadêmico
            recipients: Lista de números para enviar (None = todos)
        
        Returns:
            Lista de confirmações de envio
        """
        message = f"""
📚 *ATUALIZAÇÃO DE HORÁRIO*

Curso: {course.upper()}
Período: {year}

Os horários foram atualizados!

📅 Acesse o Google Drive para ver a versão mais recente:
https://drive.google.com/folder/horarios

Se tiver dúvidas, entre em contato com a secretaria.

---
Sistema de Gerenciamento de Horários
        """.strip()
        
        results = []
        
        if recipients:
            phones = recipients
        else:
            phones = list(self.contacts.keys())
        
        for phone in phones:
            result = self.send_message(
                phone,
                message,
                MessageType.SCHEDULE_UPDATE
            )
            if result:
                results.append(result)
        
        return results
    
    def send_weekly_schedule(self, course: str, week_info: Dict,
                            recipients: List[str] = None) -> List[Dict]:
        """
        Envia horário da semana
        
        Args:
            course: Nome do curso
            week_info: Informações da semana
            recipients: Lista de números para enviar
        
        Returns:
            Lista de confirmações de envio
        """
        message = f"""
📅 *HORÁRIO DA SEMANA*

Curso: {course.upper()}
Semana: {week_info.get('week_number', 'N/A')}

*SEGUNDA-FEIRA*
19:00 - 20:40: {week_info.get('monday_1', 'Sem aula')}
21:00 - 22:40: {week_info.get('monday_2', 'Sem aula')}

*QUARTA-FEIRA*
19:00 - 20:40: {week_info.get('wednesday_1', 'Sem aula')}
21:00 - 22:40: {week_info.get('wednesday_2', 'Sem aula')}

Local: {week_info.get('location', 'A confirmar')}

---
Sistema de Gerenciamento de Horários
        """.strip()
        
        results = []
        
        if recipients:
            phones = recipients
        else:
            phones = list(self.contacts.keys())
        
        for phone in phones:
            result = self.send_message(
                phone,
                message,
                MessageType.WEEKLY_SCHEDULE
            )
            if result:
                results.append(result)
        
        return results
    
    def send_holiday_alert(self, holiday_name: str, date: str,
                          recipients: List[str] = None) -> List[Dict]:
        """
        Envia alerta de feriado
        
        Args:
            holiday_name: Nome do feriado
            date: Data do feriado
            recipients: Lista de números para enviar
        
        Returns:
            Lista de confirmações de envio
        """
        message = f"""
🎉 *ALERTA DE FERIADO*

{holiday_name}
Data: {date}

Não haverá aulas nesta data.

Próximas aulas:
📅 Consulte o calendário acadêmico

---
Sistema de Gerenciamento de Horários
        """.strip()
        
        results = []
        
        if recipients:
            phones = recipients
        else:
            phones = list(self.contacts.keys())
        
        for phone in phones:
            result = self.send_message(
                phone,
                message,
                MessageType.HOLIDAY_ALERT
            )
            if result:
                results.append(result)
        
        return results
    
    def send_broadcast(self, message: str, group_name: str = None) -> List[Dict]:
        """
        Envia mensagem em broadcast
        
        Args:
            message: Conteúdo da mensagem
            group_name: Nome do grupo (None = todos)
        
        Returns:
            Lista de confirmações de envio
        """
        results = []
        
        for phone in self.contacts.keys():
            result = self.send_message(phone, message)
            if result:
                results.append(result)
        
        return results
    
    def get_message_history(self, phone: str = None) -> List[Dict]:
        """
        Retorna histórico de mensagens
        
        Args:
            phone: Filtrar por número (None = todas)
        
        Returns:
            Lista de mensagens
        """
        if phone:
            return [m for m in self.sent_messages if m['to'] == phone]
        return self.sent_messages
    
    def get_contacts_summary(self) -> Dict:
        """Retorna resumo de contatos"""
        return {
            'total_contacts': len(self.contacts),
            'contacts': self.contacts,
            'total_messages_sent': len(self.sent_messages)
        }


class ScheduleNotificationScheduler:
    """Agenda notificações de horários"""
    
    def __init__(self, bot: WhatsAppBot):
        self.bot = bot
        self.scheduled_notifications = []
    
    def schedule_weekly_update(self, day_of_week: str, time: str,
                              course: str) -> Dict:
        """
        Agenda atualização semanal
        
        Args:
            day_of_week: Dia da semana (segunda, terça, etc)
            time: Hora (HH:MM)
            course: Curso
        
        Returns:
            Dict com informações da agenda
        """
        notification = {
            'id': f'notif_{datetime.now().timestamp()}',
            'type': 'weekly_update',
            'day': day_of_week,
            'time': time,
            'course': course,
            'created_at': datetime.now().isoformat(),
            'status': 'scheduled'
        }
        
        self.scheduled_notifications.append(notification)
        
        print(f"[✓] Notificação agendada: {day_of_week} às {time}")
        return notification
    
    def schedule_holiday_alert(self, holiday_name: str, date: str) -> Dict:
        """
        Agenda alerta de feriado
        
        Args:
            holiday_name: Nome do feriado
            date: Data do feriado
        
        Returns:
            Dict com informações da agenda
        """
        notification = {
            'id': f'notif_{datetime.now().timestamp()}',
            'type': 'holiday_alert',
            'holiday': holiday_name,
            'date': date,
            'created_at': datetime.now().isoformat(),
            'status': 'scheduled'
        }
        
        self.scheduled_notifications.append(notification)
        
        print(f"[✓] Alerta de feriado agendado: {holiday_name} em {date}")
        return notification
    
    def get_scheduled_notifications(self) -> List[Dict]:
        """Retorna notificações agendadas"""
        return self.scheduled_notifications


def main():
    """Teste do bot"""
    print("=" * 80)
    print("TESTE - BOT WHATSAPP")
    print("=" * 80)
    
    # Criar bot
    bot = WhatsAppBot()
    
    # Adicionar contatos
    print("\n[1] Adicionando contatos...")
    bot.add_contact("Prof. João Silva", "+55 31 99999-0001", "professor")
    bot.add_contact("Prof. Maria Santos", "+55 31 99999-0002", "professor")
    bot.add_contact("Secretaria", "+55 31 99999-0003", "secretaria")
    
    # Criar grupo
    print("\n[2] Criando grupo de professores...")
    professors = [
        {'name': 'Prof. Carlos', 'phone': '+55 31 99999-0004'},
        {'name': 'Prof. Ana', 'phone': '+55 31 99999-0005'},
    ]
    bot.add_group("Professores Criminologia", professors)
    
    # Enviar atualização de horário
    print("\n[3] Enviando atualização de horário...")
    bot.send_schedule_update("criminologia", "2026-2027")
    
    # Enviar horário da semana
    print("\n[4] Enviando horário da semana...")
    week_info = {
        'week_number': 1,
        'monday_1': 'Criminologia Geral',
        'monday_2': 'Crime e Violência',
        'wednesday_1': 'Direitos Humanos',
        'wednesday_2': 'Legislação Penal',
        'location': 'Sala 101'
    }
    bot.send_weekly_schedule("criminologia", week_info)
    
    # Enviar alerta de feriado
    print("\n[5] Enviando alerta de feriado...")
    bot.send_holiday_alert("Tiradentes", "21 de abril")
    
    # Agendar notificações
    print("\n[6] Agendando notificações...")
    scheduler = ScheduleNotificationScheduler(bot)
    scheduler.schedule_weekly_update("segunda-feira", "17:00", "criminologia")
    scheduler.schedule_holiday_alert("Corpus Christi", "04 de junho")
    
    # Resumo
    print("\n[7] Resumo de contatos:")
    summary = bot.get_contacts_summary()
    print(f"  Total de contatos: {summary['total_contacts']}")
    print(f"  Total de mensagens enviadas: {summary['total_messages_sent']}")
    
    print("\n[8] Histórico de mensagens:")
    history = bot.get_message_history()
    for msg in history[:3]:
        print(f"  - Para: {msg['to']}")
        print(f"    Tipo: {msg['type']}")
        print(f"    Hora: {msg['sent_at']}")


if __name__ == "__main__":
    main()
