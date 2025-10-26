# 📥 Telegram Manga Downloader

Um script em Python que **baixa capítulos de mangás de um canal do Telegram** e **extrai automaticamente as páginas** (de arquivos `.pdf`, `.zip` ou `.cbz`) em imagens organizadas por capítulo.

---

## 🚀 Funcionalidades

- Conecta-se automaticamente a um canal do Telegram usando a biblioteca **Telethon**.  
- Faz o **download de novos capítulos** (PDF, CBZ, ZIP).  
- Extrai páginas de PDFs e arquivos compactados.  
- Organiza os capítulos por nome do mangá e número do capítulo.  
- Registra logs detalhados de todas as operações.

---

## 🧰 Requisitos

- Python **3.10+**
- Conta e **API ID / API HASH** do [Telegram Developer Portal](https://my.telegram.org/apps)
- Pacotes Python listados abaixo:

```bash
pip install -r requirements.txt
