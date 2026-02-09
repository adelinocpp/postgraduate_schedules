# Sistema de Gerenciamento de Horários - Versão 2.0

## Visão Geral

Sistema completo e automatizado para gerenciamento de horários dos cursos de pós-graduação com integração a Google Drive, Bot WhatsApp e gerenciamento de feriados.
<!-- **Criminologia** e **GESPIN** (Gestão em Segurança Pública e Inteligência Aplicada), -->

**Versão**: 2.0  
**Data**: 09 de Fevereiro de 2026  
**Status**: Pronto para Implementação

---

## 🎯 Funcionalidades Principais

### 1. Gerenciamento de Feriados e Pontos Facultativos
- ✅ Carregamento automático de lista de feriados (MG 2026)
- ✅ Marcação automática no calendário
- ✅ Diferenciação entre feriados nacionais e pontos facultativos
- ✅ Cálculo automático de dias úteis

### 2. Integração com Google Drive
- ✅ Upload automático de horários
- ✅ Versionamento de arquivos
- ✅ Compartilhamento com professores e secretaria
- ✅ Histórico de alterações
- ✅ Backup automático

### 3. Bot WhatsApp
- ✅ Notificações de atualização de horários
- ✅ Envio de horário semanal
- ✅ Alertas de feriados
- ✅ Agendamento de mensagens
- ✅ Grupos de contatos

### 4. Geração de Horários
- ✅ Distribuição automática de disciplinas
- ✅ Respeito a restrições de horário
- ✅ Balanceamento de carga
- ✅ Validação de conflitos

### 5. Exportação Múltiplos Formatos
- ✅ JSON (para integração)
- ✅ ODS (para edição)
- ✅ PDF (para impressão)
- ✅ CSV (para análise)

---

## 📦 Componentes do Sistema

### Módulos Principais

#### `schedule_manager.py`
Gerenciador central do sistema com 5 componentes:
- **CalendarValidator**: Valida calendários acadêmicos
- **DisciplineAnalyzer**: Analisa distribuição de disciplinas
- **ScheduleGenerator**: Gera horários automaticamente
- **ConflictValidator**: Valida conflitos de horários
- **ScheduleExporter**: Exporta em múltiplos formatos

#### `holiday_manager.py`
Gerenciamento de feriados e pontos facultativos:
- **HolidayManager**: Carrega e gerencia feriados
- **CalendarWithHolidays**: Gera calendário com feriados marcados

#### `google_drive_manager.py`
Integração com Google Drive:
- **GoogleDriveManager**: Upload, compartilhamento e backup
- **VersionManager**: Gerencia versões de horários

#### `whatsapp_bot.py`
Bot para notificações via WhatsApp:
- **WhatsAppBot**: Envia mensagens e gerencia contatos
- **ScheduleNotificationScheduler**: Agenda notificações

#### `config.py`
Configuração centralizada do sistema

---

## 🚀 Instalação

### Pré-requisitos
```bash
Python 3.11+
pip
```

### Dependências
```bash
pip install pandas
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client  # Google Drive
pip install twilio  # WhatsApp (Twilio)
pip install reportlab  # PDF
pip install odfpy  # ODS
```

### Configuração Inicial

1. **Clone ou baixe os arquivos do projeto**
```bash
cd /home/ubuntu/projects/horarios-p-s-acadepol-6f451624/
```

2. **Configure as credenciais (opcional)**

#### Google Drive
```bash
# 1. Acesse https://console.cloud.google.com/
# 2. Crie um novo projeto
# 3. Ative a API do Google Drive
# 4. Crie credenciais OAuth 2.0
# 5. Salve como 'credentials.json'
```

#### WhatsApp (Twilio)
```bash
# 1. Crie conta em https://www.twilio.com/
# 2. Obtenha Account SID e Auth Token
# 3. Configure em config.py
```

3. **Teste a instalação**
```bash
python3 schedule_manager.py
python3 holiday_manager.py
python3 google_drive_manager.py
python3 whatsapp_bot.py
```

---

## 📖 Guia de Uso

### Uso Básico

#### 1. Gerar Horários
```python
from schedule_manager import ScheduleManager

manager = ScheduleManager('criminologia', '2026-2027')
results = manager.process(
    'CAL_2026-2027_Calendario.csv',
    'DIST_2026-2027_Criminologia.csv'
)
```

#### 2. Gerenciar Feriados
```python
from holiday_manager import HolidayManager, CalendarWithHolidays

# Carregar feriados
holidays = HolidayManager('Lista_feriados_ponto_facultativo.txt')

# Gerar calendário com feriados
cal = CalendarWithHolidays(2026, 'Lista_feriados_ponto_facultativo.txt')
calendar = cal.generate_calendar()
```

#### 3. Integrar com Google Drive
```python
from google_drive_manager import GoogleDriveManager, VersionManager

# Criar gerenciador
drive_mgr = GoogleDriveManager('credentials.json', 'folder_id')

# Fazer upload
file_info = drive_mgr.upload_file('schedule.json', 'Horário_v1.json')

# Gerenciar versões
version_mgr = VersionManager(drive_mgr)
v1 = version_mgr.create_schedule_version('criminologia', '2026-2027', data)
```

#### 4. Enviar Notificações WhatsApp
```python
from whatsapp_bot import WhatsAppBot, ScheduleNotificationScheduler

# Criar bot
bot = WhatsAppBot('api_key', '+55 31 99999-0000')

# Adicionar contatos
bot.add_contact('Prof. João', '+55 31 99999-0001', 'professor')

# Enviar atualização
bot.send_schedule_update('criminologia', '2026-2027')

# Agendar notificações
scheduler = ScheduleNotificationScheduler(bot)
scheduler.schedule_weekly_update('segunda-feira', '17:00', 'criminologia')
```

---

## ⚙️ Configuração

Edite `config.py` para personalizar:

```python
# Ativar Google Drive
GOOGLE_DRIVE_CONFIG = {
    'enabled': True,
    'credentials_file': 'credentials.json',
    'folder_name': 'Horários Pós-Graduação 2026-2027'
}

# Ativar WhatsApp
WHATSAPP_CONFIG = {
    'enabled': True,
    'api_provider': 'twilio',
    'send_schedule_updates': True,
    'schedule_update_day': 'segunda-feira',
    'schedule_update_time': '17:00'
}
```

---

## 📊 Estrutura de Dados

### Calendário
```json
{
  "date": "01/03/2026",
  "day_of_week": "Monday",
  "is_holiday": false,
  "is_optional_holiday": false,
  "holiday_name": null
}
```

### Horário
```json
{
  "course": "criminologia",
  "year": "2026-2027",
  "type": "weekly",
  "semester": "sem1",
  "capacity": 64,
  "slots": [
    {
      "day": "segunda",
      "time": "19:00-20:40",
      "duration": 100
    }
  ]
}
```

### Versão
```json
{
  "version": 1,
  "course": "criminologia",
  "year": "2026-2027",
  "created_at": "2026-02-09T12:00:00",
  "notes": "Versão inicial",
  "drive_id": "v1_1234567890"
}
```

---

## 🔄 Fluxo de Trabalho Recomendado

1. **Validar Calendário** → `CalendarValidator`
2. **Carregar Feriados** → `HolidayManager`
3. **Analisar Disciplinas** → `DisciplineAnalyzer`
4. **Gerar Horários** → `ScheduleGenerator`
5. **Validar Conflitos** → `ConflictValidator`
6. **Criar Versão** → `VersionManager`
7. **Fazer Upload** → `GoogleDriveManager`
8. **Compartilhar** → `GoogleDriveManager.share_file()`
9. **Notificar** → `WhatsAppBot`
10. **Agendar** → `ScheduleNotificationScheduler`

---

## 📋 Checklist de Implementação

- [ ] Instalar dependências Python
- [ ] Configurar credenciais Google Drive
- [ ] Configurar API WhatsApp (Twilio)
- [ ] Testar módulo de feriados
- [ ] Testar geração de horários
- [ ] Testar integração Google Drive
- [ ] Testar bot WhatsApp
- [ ] Criar banco de dados (opcional)
- [ ] Documentar contatos WhatsApp
- [ ] Configurar agendamento de tarefas

---

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'pandas'"
```bash
pip install pandas
```

### Erro: "Google Drive authentication failed"
- Verifique se `credentials.json` existe
- Confirme permissões da API do Google Drive
- Regenere as credenciais

### Erro: "WhatsApp API not responding"
- Verifique credenciais da Twilio
- Confirme número de telefone do bot
- Verifique limite de requisições da API

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Consulte a documentação do projeto
2. Verifique os logs em `logs/system.log`
3. Entre em contato com a equipe de desenvolvimento

---

## 📝 Licença

Sistema desenvolvido para Acadepol - Pós-Graduação em Criminologia e GESPIN

---

## 🔄 Histórico de Versões

| Versão | Data | Alterações |
|--------|------|-----------|
| 2.0 | 09/02/2026 | Adicionado: Feriados, Google Drive, WhatsApp |
| 1.0 | 09/02/2026 | Versão inicial com gerenciamento básico |

---

**Desenvolvido com ❤️ para Acadepol**
