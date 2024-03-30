import telebot
import threading
import subprocess
import os
import requests
import json

def ler_chave_api():
    with open('chave_api.txt', 'r') as file:
        return file.read().strip()

chave_api = ler_chave_api()
bot = telebot.TeleBot(chave_api)

def meu_ip(chat_id):
    try:
        response = requests.get('https://api.ipify.org?format=json')
        ip = response.json()['ip']
        bot.send_message(chat_id, f"Seu endereço IP atual é: {ip}")
    except Exception as e:
        bot.send_message(chat_id, f"Ocorreu um erro ao obter o endereço IP: {e}")

def localizar_ip(ip, chat_id):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data['status'] == 'success':
            mensagem = f"Informações sobre o endereço IP {ip}:\n"
            if 'district' in data:
                mensagem += f"Bairro: {data['district']}\n"
            mensagem += f"Cidade: {data['city']}\n"
            mensagem += f"Estado: {data['regionName']} ({data['region']})\n"
            mensagem += f"País: {data['country']}\n"
            bot.send_message(chat_id, mensagem)
        else:
            bot.send_message(chat_id, "Não foi possível localizar informações para o endereço IP fornecido.")
    except Exception as e:
        bot.send_message(chat_id, f"Ocorreu um erro ao localizar o endereço IP: {e}")

def consultar_cep(cep, chat_id):
    try:
        url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(url)
        data = response.json()
        
        if 'erro' not in data:
            endereco = f"Seu endereço é:\n"
            endereco += f"CEP: {data['cep']}\n"
            endereco += f"Logradouro: {data['logradouro']}\n"
            endereco += f"Complemento: {data.get('complemento', 'N/A')}\n"
            endereco += f"Bairro: {data['bairro']}\n"
            endereco += f"Cidade: {data['localidade']}\n"
            endereco += f"Estado: {data['uf']}\n"
            bot.send_message(chat_id, endereco)
        else:
            bot.send_message(chat_id, "CEP não encontrado. Por favor, verifique o CEP e tente novamente.")
    except Exception as e:
        bot.send_message(chat_id, f"Ocorreu um erro durante a busca do endereço: {e}")

def download_spotfy(termo_busca, chat_id):
    try:
        bot.send_message(chat_id, "Procurando, só um instante...")
        subprocess.run(['spotdl', termo_busca])
        downloaded_files = [f for f in os.listdir() if f.endswith('.mp3')]
        for file_name in downloaded_files:
            original_file_path = os.path.join(os.getcwd(), file_name)
            new_file_name = f"{termo_busca.replace(' ', '_')}.mp3"  # Substitui espaços por underscores
            new_file_path = os.path.join(os.getcwd(), new_file_name)
            os.rename(original_file_path, new_file_path)
        if os.path.exists(new_file_path):
            bot.send_message(chat_id, "Áudio extraído com sucesso!")
            with open(new_file_path, 'rb') as audio:
                bot.send_audio(chat_id, audio)
            os.remove(new_file_path)
        else:
            bot.send_message(chat_id, "Desculpe, ocorreu um erro durante o processo. Tente novamente mais tarde.")
    except Exception as e:
        bot.send_message(chat_id, f"Ocorreu um erro durante o download: {e}")

@bot.message_handler(commands=['start'])
def handle_start(message):
    mensagem = ("Olá! 😊\n"
                "Meu nome é Tais Brito e estou aqui para ser sua assistente pessoal no Telegram!\n\n"
                "Estou aqui para ajudar você no que precisar. Se tiver dúvidas ou precisar de alguma coisa, "
                "é só me chamar! Use o comando /ajuda para ver o que posso fazer por você.")
    bot.reply_to(message, mensagem)

@bot.message_handler(commands=['ajuda'])
def handle_help(message):
    # Mensagem de ajuda
    mensagem = ("Aqui estão alguns comandos que você pode usar para interagir comigo:\n"
                "/meuip - Mostra o seu endereço IP atual.\n"
                "/cep - Consulta informações sobre um CEP.\n"
                "/bs - Busca e baixa uma música no Spotify.")
    bot.reply_to(message, mensagem)
@bot.message_handler(commands=["meuip"])
def handle_meuip_command(message):
    chat_id = message.chat.id
    threading.Thread(target=meu_ip, args=(chat_id,)).start()

@bot.message_handler(commands=["cep"])
def handle_cep_command(message):
    bot.reply_to(message, "Por favor, digite o CEP que você deseja consultar:")
    bot.register_next_step_handler(message, handle_cep)

@bot.message_handler(commands=["bs"])
def handle_bs_command(message):
    bot.reply_to(message, "Por favor, digite os termos de busca para que eu possa baixar e enviar sua música:")
    bot.register_next_step_handler(message, handle_search_term)

def handle_cep(message):
    cep = message.text
    chat_id = message.chat.id
    threading.Thread(target=consultar_cep, args=(cep, chat_id)).start()

def handle_search_term(message):
    search_term = message.text
    chat_id = message.chat.id
    threading.Thread(target=download_spotfy, args=(search_term, chat_id)).start()

bot.polling()