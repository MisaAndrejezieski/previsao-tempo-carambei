import json
import os
import time
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta
from tkinter import messagebox, scrolledtext, ttk

import folium
import requests


class PrevisaoTempoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Previsão do Tempo - Seu Clima Neon")
        self.root.geometry("950x800")
        self.root.resizable(True, True)
        
        # Cores neon pasteis
        self.cores = {
            'bg': '#1a1a2e',
            'bg_frame': '#16213e',
            'neon_rosa': '#ff6b9d',
            'neon_azul': '#4ecdc4',
            'neon_verde': '#7bed9f',
            'neon_roxo': '#a29bfe',
            'neon_amarelo': '#ffeaa7',
            'neon_laranja': '#fd79a8',
            'texto_claro': '#dfe6e9',
            'texto_escuro': '#2d3436',
            'status_bg': '#2d2d44',
            'neon_vermelho': '#ff4757'
        }
        
        # Configurar fundo da janela
        self.root.configure(bg=self.cores['bg'])
        
        # Frame principal
        main_frame = tk.Frame(root, bg=self.cores['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Título
        titulo_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        titulo_frame.grid(row=0, column=0, pady=(0, 10))
        
        titulo = tk.Label(titulo_frame, 
                         text="🌤️ PREVISÃO DO TEMPO NEON 🌤️",
                         font=('Segoe UI', 20, 'bold'),
                         fg=self.cores['neon_azul'],
                         bg=self.cores['bg'])
        titulo.pack()
        
        subtitulo = tk.Label(titulo_frame,
                            text="✦ Dados precisos da Open-Meteo API com mapa interativo ✦",
                            font=('Segoe UI', 11, 'italic'),
                            fg=self.cores['neon_roxo'],
                            bg=self.cores['bg'])
        subtitulo.pack()
        
        # Frame de busca
        search_frame = tk.Frame(main_frame, bg=self.cores['bg_frame'], 
                               relief=tk.RAISED, bd=2)
        search_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Label da cidade
        label_cidade = tk.Label(search_frame,
                               text="🌆 Cidade:",
                               font=('Segoe UI', 11, 'bold'),
                               fg=self.cores['neon_verde'],
                               bg=self.cores['bg_frame'])
        label_cidade.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Entry para digitar a cidade
        self.cidade_var = tk.StringVar()
        self.cidade_var.set("Carambeí")
        self.entry_cidade = tk.Entry(search_frame,
                                     textvariable=self.cidade_var,
                                     font=('Segoe UI', 11),
                                     width=25,
                                     bg=self.cores['bg'],
                                     fg=self.cores['texto_claro'],
                                     insertbackground=self.cores['neon_verde'],
                                     relief=tk.FLAT)
        self.entry_cidade.pack(side=tk.LEFT, padx=5, pady=10)
        self.entry_cidade.bind('<Return>', lambda e: self.buscar_cidade())
        
        # Botão de buscar
        self.btn_buscar = tk.Button(search_frame,
                                   text="🔍 Buscar Clima",
                                   font=('Segoe UI', 10, 'bold'),
                                   fg=self.cores['bg'],
                                   bg=self.cores['neon_azul'],
                                   activebackground=self.cores['neon_verde'],
                                   activeforeground=self.cores['bg'],
                                   relief=tk.FLAT,
                                   padx=15,
                                   pady=8,
                                   cursor='hand2',
                                   command=self.buscar_cidade)
        self.btn_buscar.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Sugestões rápidas
        sugestoes_frame = tk.Frame(search_frame, bg=self.cores['bg_frame'])
        sugestoes_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        tk.Label(sugestoes_frame,
                text="Sugestões:",
                font=('Segoe UI', 9),
                fg=self.cores['neon_amarelo'],
                bg=self.cores['bg_frame']).pack(side=tk.LEFT, padx=5)
        
        cidades_sugeridas = ["Carambeí", "Curitiba", "São Paulo", "Rio de Janeiro", "Brasília", "Porto Alegre"]
        for cidade in cidades_sugeridas:
            btn_sug = tk.Button(sugestoes_frame,
                               text=cidade,
                               font=('Segoe UI', 8),
                               fg=self.cores['bg'],
                               bg=self.cores['neon_roxo'],
                               activebackground=self.cores['neon_azul'],
                               activeforeground=self.cores['bg'],
                               relief=tk.FLAT,
                               padx=8,
                               pady=3,
                               cursor='hand2',
                               command=lambda c=cidade: self.set_cidade(c))
            btn_sug.pack(side=tk.LEFT, padx=3)
        
        # Frame para botões principais
        button_frame = tk.Frame(main_frame, bg=self.cores['bg_frame'], 
                               relief=tk.RAISED, bd=2)
        button_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.btn_atualizar = tk.Button(button_frame, 
                                      text="🔄 Atualizar Clima",
                                      font=('Segoe UI', 10, 'bold'),
                                      fg=self.cores['bg'],
                                      bg=self.cores['neon_verde'],
                                      activebackground=self.cores['neon_azul'],
                                      activeforeground=self.cores['bg'],
                                      relief=tk.FLAT,
                                      padx=15,
                                      pady=8,
                                      cursor='hand2',
                                      command=self.atualizar_clima)
        self.btn_atualizar.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_detalhes = tk.Button(button_frame,
                                     text="📊 Detalhes Completos",
                                     font=('Segoe UI', 10, 'bold'),
                                     fg=self.cores['bg'],
                                     bg=self.cores['neon_roxo'],
                                     activebackground=self.cores['neon_azul'],
                                     activeforeground=self.cores['bg'],
                                     relief=tk.FLAT,
                                     padx=15,
                                     pady=8,
                                     cursor='hand2',
                                     command=self.mostrar_detalhes)
        self.btn_detalhes.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_previsao = tk.Button(button_frame,
                                     text="📅 Previsão 7 Dias",
                                     font=('Segoe UI', 10, 'bold'),
                                     fg=self.cores['bg'],
                                     bg=self.cores['neon_laranja'],
                                     activebackground=self.cores['neon_rosa'],
                                     activeforeground=self.cores['bg'],
                                     relief=tk.FLAT,
                                     padx=15,
                                     pady=8,
                                     cursor='hand2',
                                     command=self.mostrar_previsao_semana)
        self.btn_previsao.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_mapa = tk.Button(button_frame,
                                 text="🗺️ Ver Mapa",
                                 font=('Segoe UI', 10, 'bold'),
                                 fg=self.cores['bg'],
                                 bg=self.cores['neon_amarelo'],
                                 activebackground=self.cores['neon_roxo'],
                                 activeforeground=self.cores['bg'],
                                 relief=tk.FLAT,
                                 padx=15,
                                 pady=8,
                                 cursor='hand2',
                                 command=self.gerar_mapa)
        self.btn_mapa.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.btn_limpar = tk.Button(button_frame,
                                   text="🗑️ Limpar",
                                   font=('Segoe UI', 10, 'bold'),
                                   fg=self.cores['bg'],
                                   bg=self.cores['neon_rosa'],
                                   activebackground=self.cores['neon_laranja'],
                                   activeforeground=self.cores['bg'],
                                   relief=tk.FLAT,
                                   padx=15,
                                   pady=8,
                                   cursor='hand2',
                                   command=self.limpar_texto)
        self.btn_limpar.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.cores['bg_frame'])
        status_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("✨ Pronto para consultar ✨")
        self.status_bar = tk.Label(status_frame,
                                   textvariable=self.status_var,
                                   font=('Segoe UI', 9, 'italic'),
                                   fg=self.cores['neon_azul'],
                                   bg=self.cores['bg_frame'],
                                   anchor=tk.W,
                                   padx=10,
                                   pady=5)
        self.status_bar.pack(fill=tk.X)
        
        # Área de texto
        text_frame = tk.Frame(main_frame, bg=self.cores['bg_frame'], 
                            relief=tk.RAISED, bd=2)
        text_frame.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.text_area = scrolledtext.ScrolledText(text_frame,
                                                  wrap=tk.WORD,
                                                  width=80,
                                                  height=22,
                                                  font=('Consolas', 10),
                                                  bg=self.cores['bg'],
                                                  fg=self.cores['texto_claro'],
                                                  insertbackground=self.cores['neon_verde'],
                                                  relief=tk.FLAT,
                                                  padx=10,
                                                  pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar tags
        self.text_area.tag_configure('titulo', 
                                    font=('Segoe UI', 14, 'bold'),
                                    foreground=self.cores['neon_azul'])
        self.text_area.tag_configure('subtitulo',
                                    font=('Segoe UI', 12, 'bold'),
                                    foreground=self.cores['neon_roxo'])
        self.text_area.tag_configure('destaque',
                                    font=('Segoe UI', 11, 'bold'),
                                    foreground=self.cores['neon_verde'])
        self.text_area.tag_configure('info',
                                    foreground=self.cores['neon_rosa'])
        self.text_area.tag_configure('separador',
                                    foreground=self.cores['neon_amarelo'])
        self.text_area.tag_configure('erro',
                                    foreground=self.cores['neon_vermelho'],
                                    font=('Segoe UI', 10, 'bold'))
        self.text_area.tag_configure('neon_laranja',
                                    foreground=self.cores['neon_laranja'])
        
        # Variável para armazenar localização atual
        self.localizacao_atual = None
        
        # Carregar dados iniciais
        self.root.after(100, self.atualizar_clima)
    
    def geocodificar(self, cidade):
        """Converte nome da cidade em coordenadas usando Open-Meteo Geocoding"""
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={cidade}&count=1&language=pt&format=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                if dados.get('results'):
                    resultado = dados['results'][0]
                    return {
                        'nome': resultado['name'],
                        'pais': resultado.get('country', 'N/A'),
                        'latitude': resultado['latitude'],
                        'longitude': resultado['longitude'],
                        'regiao': resultado.get('admin1', 'N/A')
                    }
            return None
        except Exception as e:
            return None
    
    def buscar_dados_clima(self, lat, lon):
        """Busca dados climáticos da Open-Meteo API"""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=America/Sao_Paulo&forecast_days=7"
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            return None
    
    def traduzir_clima(self, weather_code):
        """Traduz o código WMO para texto em português"""
        codigos = {
            0: "☀️ Céu limpo",
            1: "🌤️ Principalmente limpo",
            2: "⛅ Parcialmente nublado",
            3: "☁️ Encoberto",
            45: "🌫️ Nevoeiro",
            48: "🌫️ Nevoeiro gelado",
            51: "🌧️ Chuvisco leve",
            53: "🌧️ Chuvisco moderado",
            55: "🌧️ Chuvisco forte",
            61: "🌧️ Chuva leve",
            63: "🌧️ Chuva moderada",
            65: "🌧️ Chuva forte",
            71: "❄️ Neve leve",
            73: "❄️ Neve moderada",
            75: "❄️ Neve forte",
            80: "🌧️ Aguaceiros leves",
            81: "🌧️ Aguaceiros moderados",
            82: "🌧️ Aguaceiros fortes",
            95: "⛈️ Trovoada",
            96: "⛈️ Trovoada com granizo",
            99: "⛈️ Trovoada forte com granizo"
        }
        return codigos.get(weather_code, f"Código {weather_code}")
    
    def buscar_cidade(self):
        """Busca o clima para a cidade digitada"""
        cidade = self.cidade_var.get().strip()
        if cidade:
            self.status_var.set(f"🌟 Buscando clima para {cidade}... 🌟")
            self.root.update()
            self.atualizar_clima()
        else:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "⚠️ Por favor, digite o nome de uma cidade!\n", 'erro')
            self.status_var.set("⚠️ Digite o nome da cidade")
    
    def set_cidade(self, cidade):
        """Define a cidade e busca automaticamente"""
        self.cidade_var.set(cidade)
        self.buscar_cidade()
    
    def atualizar_clima(self):
        """Atualiza a previsão do tempo resumida"""
        self.text_area.delete(1.0, tk.END)
        cidade = self.cidade_var.get().strip()
        
        if not cidade:
            self.text_area.insert(tk.END, "⚠️ Digite o nome de uma cidade!\n", 'erro')
            self.status_var.set("⚠️ Digite o nome da cidade")
            return
        
        self.status_var.set(f"🌟 Buscando {cidade}... 🌟")
        self.root.update()
        
        # Geocodificar
        localizacao = self.geocodificar(cidade)
        if not localizacao:
            self.text_area.insert(tk.END, f"❌ Cidade '{cidade}' não encontrada!\n", 'erro')
            self.text_area.insert(tk.END, "Verifique o nome e tente novamente.\n", 'info')
            self.status_var.set("❌ Cidade não encontrada")
            return
        
        self.localizacao_atual = localizacao
        
        # Buscar clima
        dados_clima = self.buscar_dados_clima(localizacao['latitude'], localizacao['longitude'])
        if not dados_clima:
            self.text_area.insert(tk.END, "❌ Erro ao buscar dados climáticos!\n", 'erro')
            self.status_var.set("❌ Erro ao buscar dados")
            return
        
        # Extrair dados atuais
        current = dados_clima.get('current', {})
        temp = current.get('temperature_2m', 'N/A')
        sensacao = current.get('apparent_temperature', 'N/A')
        umidade = current.get('relative_humidity_2m', 'N/A')
        vento = current.get('wind_speed_10m', 'N/A')
        precip = current.get('precipitation', 'N/A')
        weather_code = current.get('weather_code', 0)
        condicao = self.traduzir_clima(weather_code)
        
        # Mostrar resultado
        self.text_area.insert(tk.END, "✦" * 35 + "\n", 'separador')
        self.text_area.insert(tk.END, f"  🌸 {localizacao['nome'].upper()} - {localizacao['pais']} 🌸\n", 'titulo')
        self.text_area.insert(tk.END, "✦" * 35 + "\n\n", 'separador')
        
        self.text_area.insert(tk.END, f"  {condicao}\n\n", 'destaque')
        self.text_area.insert(tk.END, f"  🌡️  Temperatura: {temp}°C\n", 'neon_laranja')
        self.text_area.insert(tk.END, f"  🌡️  Sensação: {sensacao}°C\n", 'info')
        self.text_area.insert(tk.END, f"  💧  Umidade: {umidade}%\n", 'info')
        self.text_area.insert(tk.END, f"  💨  Vento: {vento} km/h\n", 'info')
        self.text_area.insert(tk.END, f"  🌧️  Precipitação: {precip} mm\n\n", 'info')
        
        self.text_area.insert(tk.END, "✦" * 35 + "\n", 'separador')
        self.text_area.insert(tk.END, "  💫 Para mais informações:\n", 'info')
        self.text_area.insert(tk.END, "  📊 'Detalhes Completos'\n", 'neon_laranja')
        self.text_area.insert(tk.END, "  📅 'Previsão 7 Dias'\n", 'neon_laranja')
        self.text_area.insert(tk.END, "  🗺️ 'Ver Mapa' para visualizar no mapa\n", 'neon_laranja')
        self.text_area.insert(tk.END, "✦" * 35 + "\n", 'separador')
        
        self.status_var.set(f"✨ {localizacao['nome']} atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ✨")
    
    def mostrar_detalhes(self):
        """Mostra os detalhes completos"""
        cidade = self.cidade_var.get().strip()
        
        if not cidade:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "⚠️ Digite o nome de uma cidade!\n", 'erro')
            self.status_var.set("⚠️ Digite o nome da cidade")
            return
        
        self.status_var.set(f"🌟 Carregando detalhes para {cidade}... 🌟")
        self.root.update()
        
        localizacao = self.geocodificar(cidade)
        if not localizacao:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"❌ Cidade '{cidade}' não encontrada!\n", 'erro')
            self.status_var.set("❌ Cidade não encontrada")
            return
        
        self.localizacao_atual = localizacao
        
        dados_clima = self.buscar_dados_clima(localizacao['latitude'], localizacao['longitude'])
        if not dados_clima:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "❌ Erro ao buscar dados climáticos!\n", 'erro')
            self.status_var.set("❌ Erro ao buscar dados")
            return
        
        self.text_area.delete(1.0, tk.END)
        
        # Cabeçalho
        self.text_area.insert(tk.END, "✦" * 45 + "\n", 'separador')
        self.text_area.insert(tk.END, f"  🌸 DETALHES - {localizacao['nome'].upper()} 🌸\n", 'titulo')
        self.text_area.insert(tk.END, "✦" * 45 + "\n\n", 'separador')
        
        # Localização
        self.text_area.insert(tk.END, "📍 LOCALIZAÇÃO\n", 'subtitulo')
        self.text_area.insert(tk.END, f"  Cidade: {localizacao['nome']}\n", 'info')
        self.text_area.insert(tk.END, f"  Região: {localizacao['regiao']}\n", 'info')
        self.text_area.insert(tk.END, f"  País: {localizacao['pais']}\n", 'info')
        self.text_area.insert(tk.END, f"  Coordenadas: {localizacao['latitude']}, {localizacao['longitude']}\n\n", 'info')
        
        # Dados atuais
        current = dados_clima.get('current', {})
        self.text_area.insert(tk.END, "🌡️ CONDIÇÕES ATUAIS\n", 'subtitulo')
        
        weather_code = current.get('weather_code', 0)
        condicao = self.traduzir_clima(weather_code)
        self.text_area.insert(tk.END, f"  {condicao}\n", 'destaque')
        self.text_area.insert(tk.END, f"  🌡️  Temperatura: {current.get('temperature_2m', 'N/A')}°C\n", 'neon_laranja')
        self.text_area.insert(tk.END, f"  🌡️  Sensação térmica: {current.get('apparent_temperature', 'N/A')}°C\n", 'info')
        self.text_area.insert(tk.END, f"  💧  Umidade: {current.get('relative_humidity_2m', 'N/A')}%\n", 'info')
        self.text_area.insert(tk.END, f"  💨  Vento: {current.get('wind_speed_10m', 'N/A')} km/h\n", 'info')
        self.text_area.insert(tk.END, f"  🧭  Direção do vento: {current.get('wind_direction_10m', 'N/A')}°\n", 'info')
        self.text_area.insert(tk.END, f"  🌧️  Precipitação: {current.get('precipitation', 'N/A')} mm\n", 'info')
        self.text_area.insert(tk.END, f"  📊  Pressão: {current.get('pressure_msl', 'N/A')} hPa\n", 'info')
        self.text_area.insert(tk.END, f"  ☁️  Nebulosidade: {current.get('cloud_cover', 'N/A')}%\n\n", 'info')
        
        self.text_area.insert(tk.END, "✦" * 45 + "\n", 'separador')
        self.text_area.insert(tk.END, "💫 Dados fornecidos por Open-Meteo\n", 'info')
        self.text_area.insert(tk.END, "🗺️ Clique em 'Ver Mapa' para visualizar no mapa\n", 'info')
        self.status_var.set(f"✨ Detalhes de {localizacao['nome']} atualizados ✨")
    
    def mostrar_previsao_semana(self):
        """Mostra a previsão para 7 dias"""
        cidade = self.cidade_var.get().strip()
        
        if not cidade:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "⚠️ Digite o nome de uma cidade!\n", 'erro')
            self.status_var.set("⚠️ Digite o nome da cidade")
            return
        
        self.status_var.set(f"🌟 Carregando previsão para {cidade}... 🌟")
        self.root.update()
        
        localizacao = self.geocodificar(cidade)
        if not localizacao:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, f"❌ Cidade '{cidade}' não encontrada!\n", 'erro')
            self.status_var.set("❌ Cidade não encontrada")
            return
        
        self.localizacao_atual = localizacao
        
        dados_clima = self.buscar_dados_clima(localizacao['latitude'], localizacao['longitude'])
        if not dados_clima:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "❌ Erro ao buscar dados climáticos!\n", 'erro')
            self.status_var.set("❌ Erro ao buscar dados")
            return
        
        self.text_area.delete(1.0, tk.END)
        
        # Cabeçalho
        self.text_area.insert(tk.END, "✦" * 50 + "\n", 'separador')
        self.text_area.insert(tk.END, f"  📅 PREVISÃO 7 DIAS - {localizacao['nome'].upper()} 📅\n", 'titulo')
        self.text_area.insert(tk.END, "✦" * 50 + "\n\n", 'separador')
        
        daily = dados_clima.get('daily', {})
        datas = daily.get('time', [])
        temp_max = daily.get('temperature_2m_max', [])
        temp_min = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        weather_codes = daily.get('weather_code', [])
        
        for i in range(min(7, len(datas))):
            data_obj = datetime.strptime(datas[i], '%Y-%m-%d')
            dias_semana = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO', 'DOMINGO']
            nome_dia = dias_semana[data_obj.weekday()]
            data_formatada = data_obj.strftime('%d/%m')
            
            condicao = self.traduzir_clima(weather_codes[i] if i < len(weather_codes) else 0)
            
            self.text_area.insert(tk.END, f"  📆 {nome_dia} - {data_formatada}\n", 'destaque')
            self.text_area.insert(tk.END, f"     {condicao}\n", 'info')
            self.text_area.insert(tk.END, f"     🔥 Máx: {temp_max[i] if i < len(temp_max) else 'N/A'}°C", 'neon_laranja')
            self.text_area.insert(tk.END, f"  ❄️ Mín: {temp_min[i] if i < len(temp_min) else 'N/A'}°C\n", 'neon_laranja')
            self.text_area.insert(tk.END, f"     🌧️  Precipitação: {precip[i] if i < len(precip) else 'N/A'} mm\n\n", 'info')
        
        self.text_area.insert(tk.END, "✦" * 50 + "\n", 'separador')
        self.text_area.insert(tk.END, "💫 Dados fornecidos por Open-Meteo\n", 'info')
        self.text_area.insert(tk.END, "🗺️ Clique em 'Ver Mapa' para visualizar no mapa\n", 'info')
        self.status_var.set(f"✨ Previsão de {localizacao['nome']} atualizada ✨")
    
    def gerar_mapa(self):
        """Gera e abre um mapa interativo da cidade"""
        if not self.localizacao_atual:
            cidade = self.cidade_var.get().strip()
            if not cidade:
                messagebox.showwarning("Aviso", "Digite o nome de uma cidade primeiro!")
                return
            
            self.status_var.set(f"🌟 Buscando localização de {cidade}... 🌟")
            self.root.update()
            
            localizacao = self.geocodificar(cidade)
            if not localizacao:
                messagebox.showerror("Erro", f"Cidade '{cidade}' não encontrada!")
                return
            self.localizacao_atual = localizacao
        
        try:
            # Criar mapa
            lat = self.localizacao_atual['latitude']
            lon = self.localizacao_atual['longitude']
            nome = self.localizacao_atual['nome']
            pais = self.localizacao_atual['pais']
            
            # Criar mapa com estilo escuro neon
            mapa = folium.Map(
                location=[lat, lon],
                zoom_start=13,
                tiles='CartoDB dark_matter',
                control_scale=True
            )
            
            # Adicionar marcador personalizado
            folium.Marker(
                [lat, lon],
                popup=f'<b>{nome}</b><br>{pais}',
                tooltip=f'Clique para detalhes de {nome}',
                icon=folium.Icon(color='pink', icon='cloud', prefix='fa')
            ).add_to(mapa)
            
            # Adicionar círculo de destaque
            folium.Circle(
                [lat, lon],
                radius=1000,
                color='#ff6b9d',
                fill=True,
                fill_color='#ff6b9d',
                fill_opacity=0.2,
                popup=f'Área de {nome}'
            ).add_to(mapa)
            
            # Salvar mapa
            mapa_path = os.path.join(os.getcwd(), f'mapa_{nome}.html')
            mapa.save(mapa_path)
            
            # Abrir no navegador
            webbrowser.open(f'file://{mapa_path}')
            
            self.status_var.set(f"🗺️ Mapa de {nome} aberto no navegador")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar mapa: {str(e)}")
            self.status_var.set("❌ Erro ao gerar mapa")
    
    def limpar_texto(self):
        """Limpa a área de texto"""
        self.text_area.delete(1.0, tk.END)
        self.status_var.set("✨ Texto limpo! ✨")

def main():
    root = tk.Tk()
    app = PrevisaoTempoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()