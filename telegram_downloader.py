import os
import gc
import re
import fitz  # PyMuPDF (precisa instalar: pip install PyMuPDF)
import zipfile  # Adicionado para extrair arquivos .zip
from telethon.sync import TelegramClient
from time import sleep
from datetime import datetime
import logging

# --- CONFIGURAÇÕES - ALTERE AQUI ---
import os
from dotenv import load_dotenv
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "komga_session")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID"))
MANGA_TITLE = os.getenv("MANGA_TITLE")


CHAPTERS_DIR = os.path.expanduser('~/data')

PAGES_DIR = os.path.expanduser('~/pages')
# ------------------------------------
LOG_FILE = os.path.expanduser('~/downloader.log')
# ------------------------------------

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)


os.makedirs(CHAPTERS_DIR, exist_ok=True)
os.makedirs(PAGES_DIR, exist_ok=True)


def log_message(message):
    """Função auxiliar para logar mensagens com timestamp."""
    logging.info(message)


def sanitize_filename(name):
    """Limpa o nome para ser usado em pastas."""
    return re.sub(r'[^a-zA-Z0-9]+', '-', name.lower())


def extract_pdf_pages(pdf_path, output_dir, quality=85):
    """Extrai todas as páginas de um arquivo PDF como imagens JPG."""
    if not os.path.exists(pdf_path):
        log_message(f"Erro: Arquivo PDF não encontrado em {pdf_path}")
        return
    os.makedirs(output_dir, exist_ok=True)
    try:
        doc = fitz.open(pdf_path)
        log_message(f"Extraindo {len(doc)} páginas de '{os.path.basename(pdf_path)}'...")
        for i, page in enumerate(doc, 1):
            pix = page.get_pixmap(dpi=150, alpha=False)
            img_path = os.path.join(output_dir, f"{i}.jpg")
            pix.save(img_path, "JPEG", jpg_quality=quality)
            pix = None
            sleep(0.1)
        doc.close()
        log_message(f"Extração de PDF concluída para '{output_dir}'")
        gc.collect()
        sleep(15)
    except Exception as e:
        log_message(f"Ocorreu um erro ao extrair o PDF '{pdf_path}': {e}")


def extract_zip_archive(zip_path, output_dir):
    """Extrai todos os arquivos de um arquivo ZIP ou CBZ."""
    if not os.path.exists(zip_path):
        log_message(f"Erro: Arquivo ZIP não encontrado em {zip_path}")
        return
    os.makedirs(output_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            log_message(f"Extraindo arquivos de '{os.path.basename(zip_path)}'...")
            zip_ref.extractall(output_dir)
        log_message(f"Extração de ZIP concluída para '{output_dir}'")
        gc.collect()
        sleep(5)
    except zipfile.BadZipFile:
        log_message(f"Erro: O arquivo '{zip_path}' não é um ZIP válido ou está corrompido.")
    except Exception as e:
        log_message(f"Ocorreu um erro ao extrair o ZIP '{zip_path}': {e}")


def main():
    log_message("=== INICIANDO EXECUÇÃO DO SCRIPT ===")
    with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        log_message("Conectado ao Telegram com sucesso.")
        existing_files = set(os.listdir(CHAPTERS_DIR))
        log_message(f"Encontrados {len(existing_files)} arquivos na pasta de capítulos.")

        messages = client.get_messages(TARGET_CHAT_ID, limit=80)
        log_message(f"Verificando as últimas {len(messages)} mensagens do canal...")

        new_downloads = 0
        new_extractions = 0

        for message in reversed(messages):
            if not message.document:
                continue

            file_name = message.document.attributes[-1].file_name
            if not (file_name.endswith(('.cbz', '.zip', '.cbr', '.pdf'))):
                continue


            if file_name not in existing_files:
                log_message(f"Baixando novo capítulo: {file_name}")
                path = os.path.join(CHAPTERS_DIR, file_name)
                client.download_media(message.media, path)
                log_message(f"'{file_name}' baixado com sucesso.")
                new_downloads += 1


            match = re.search(r"(\d+)", file_name)
            if not match:
                continue

            chapter_number = match.group(1)
            manga_dir = sanitize_filename(MANGA_TITLE)
            chapter_dir = os.path.join(PAGES_DIR, manga_dir, chapter_number)


            if not os.path.isdir(chapter_dir) or len(os.listdir(chapter_dir)) == 0:
                log_message(f"Iniciando extração para o capítulo {chapter_number} ({file_name})...")
                file_full_path = os.path.join(CHAPTERS_DIR, file_name)

                if file_name.endswith('.pdf'):
                    extract_pdf_pages(file_full_path, chapter_dir)
                    new_extractions += 1
                elif file_name.endswith(('.zip', '.cbz')):
                    extract_zip_archive(file_full_path, chapter_dir)
                    new_extractions += 1


        log_message(f"Verificação concluída. Downloads: {new_downloads}, Extrações: {new_extractions}")
        print("Verificação concluída.")
        log_message("=== FINALIZANDO EXECUÇÃO DO SCRIPT ===")

if __name__ == "__main__":
    main()
