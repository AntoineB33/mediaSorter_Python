import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'

SPREADSHEET_CONFIG = {
    'storage_path': DATA_DIR / 'spreadsheets',
    'backup_path': DATA_DIR / 'backups',
    'max_backups': 10,
}