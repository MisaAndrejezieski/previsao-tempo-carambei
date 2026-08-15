import json
import os
import pickle
import time
import tkinter as tk
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import Menu, messagebox, scrolledtext, ttk

import folium
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)


class PrevisaoTempoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌤️ PREVISÃO DO TEMPO NEON - ULTIMATE EDITION 🌤️")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.resizable(True, True)
        
        # Cores neon pasteis
        self.cores = {
            'bg': '#0a0a1a',
            'bg_frame': '#12122a',
            'bg_card': '#1a1a3e',
            'neon_rosa': '#ff6b9d',
            'neon_azul': '#4ecdc4',
            'neon_verde': '#7bed9f',
            'neon_roxo': '#a29bfe',
            'neon_amarelo': '#ffeaa7',
            'neon_laranja': '#fd79a8',
            'texto_claro': '#f0f0f0',
            'texto_escuro': '#1a1a2e',
            'status_bg': '#1a1a3e',
            'neon_vermelho': '#ff4757',
            'neon_dourado': '#ffd700',
            'neon_prata': '#c0c0c0'
        }
        
        # Configurar fundo
        self.root.configure(bg=self.cores['bg'])
        
        # Histórico e favoritos
        self.historico = []
        self.favoritos = []
        self.carregar_historico()
        self.carregar_favoritos()
        
        # Variáveis
        self.localizacao_atual = None
        self.modo_escuro = True
        
        # Criar interface
        self.criar_menu()
        self.criar_widgets()
        
        # Atualizar relógio
        self.atualizar_relogio()
        
        # Carregar cidade padrão
        self.root.after(100, self.carregar_cidade_padrao)
        
        # Atalhos de teclado
        self.configurar_atalhos()
        
        # Mostrar splash
        self.root.after(50, self.mostrar_splash)
    
    def criar_menu(self):
        """Cria a barra de menu"""
        menu_bar = Menu(self.root, bg=self.cores['bg_frame'], fg=self.cores['texto_claro'])
        self.root.config(menu=menu_bar)
        
        # Menu Arquivo
        file_menu = Menu(menu_bar, tearoff=0, bg=self.cores['bg_frame'], fg=self.cores['texto_claro'])
        menu_bar.add_cascade(label="📁 Arquivo", menu=file_menu)
        file_menu.add_command(label="📄 Exportar PDF", command=self.exportar_pdf)
        file_menu.add_command(label="🖨️ Imprimir", command=self.imprimir_relatorio)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Sair", command=self.root.quit)
        
        # Menu Clima
        clima_menu = Menu(menu_bar, tearoff=0, bg=self.cores['bg_frame'], fg=self.cores['texto_claro'])
        menu_bar.add_cascade(label="🌤️ Clima", menu=clima_menu)
        clima_menu.add_command(label="🔄 Atualizar", command=self.atualizar_clima)
        clima_menu.add_command(label="📊 Detalhes", command=self.mostrar_detalhes)
        clima_menu.add_command(label="📅 Previsão 7 Dias", command=self.mostrar_previsao_semana)
        
        # Menu Ferramentas
        tools_menu = Menu(menu_bar, tearoff=0, bg=self.cores['bg_frame'], fg=self.cores['texto_claro'])
        menu_bar.add_cascade(label="🛠️ Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="🗺️ Mapa", command=self.gerar_mapa)
        tools_menu.add_command(label="📈 Gráfico", command=self.mostrar_grafico)
        tools_menu.add_command(label="⭐ Favoritos", command=self.mostrar_favoritos)
        tools_menu.add_separator()
        tools_menu.add_command(label="🔄 Alternar Tema", command=self.alternar_tema)
        
        # Menu Ajuda
        help_menu = Menu(menu_bar, tearoff=0, bg=self.cores['bg_frame'], fg=self.cores['texto_claro'])
        menu_bar.add_cascade(label="❓ Ajuda", menu=help_menu)
        help_menu.add_command(label="📖 Sobre", command=self.mostrar_sobre)
        help_menu.add_command(label="⌨️ Atalhos", command=self.mostrar_atalhos)
    
    def configurar_atalhos(self):
        """Configura atalhos de teclado"""
        self.root.bind('<Control-d>', lambda e: self.mostrar_detalhes())
        self.root.bind('<Control-p>', lambda e: self.mostrar_previsao_semana())
        self.root.bind('<Control-m>', lambda e: self.gerar_mapa())
        self.root.bind('<Control-g>', lambda e: self.mostrar_grafico())
        self.root.bind('<Control-r>', lambda e: self.atualizar_clima())
        self.root.bind('<Control-l>', lambda e: self.limpar_texto())
        self.root.bind('<F1>', lambda e: self.mostrar_atalhos())
        self.root.bind('<Control-f>', lambda e: self.adicionar_favorito())
    
    def criar_widgets(self):
        """Cria todos os widgets da interface"""
        # Barra superior
        self.top_bar = tk.Frame(self.root, bg=self.cores['bg_frame'], height=60)
        self.top_bar.pack(fill=tk.X, pady=(0, 10))
        self.top_bar.pack_propagate(False)
        
        # Título
        titulo_label = tk.Label(self.top_bar,
                               text="🌤️ PREVISÃO DO TEMPO NEON",
                               font=('Segoe UI', 18, 'bold'),
                               fg=self.cores['neon_azul'],
                               bg=self.cores['bg_frame'])
        titulo_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Versão
        versao_label = tk.Label(self.top_bar,
                               text="v3.0 ULTIMATE",
                               font=('Segoe UI', 9, 'bold'),
                               fg=self.cores['neon_rosa'],
                               bg=self.cores['bg_frame'])
        versao_label.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Relógio
        self.relogio_label = tk.Label(self.top_bar,
                                     font=('Segoe UI', 14, 'bold'),
                                     fg=self.cores['neon_verde'],
                                     bg=self.cores['bg_frame'])
        self.relogio_label.pack(side=tk.RIGHT, padx=20, pady=10)
        
        # Frame principal
        content_frame = tk.Frame(self.root, bg=self.cores['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Coluna esquerda
        left_frame = tk.Frame(content_frame, bg=self.cores['bg'], width=320)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Frame de busca
        search_frame = tk.Frame(left_frame, bg=self.cores['bg_frame'], relief=tk.RAISED, bd=2)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame,
                text="🌆 Buscar Cidade",
                font=('Segoe UI', 12, 'bold'),
                fg=self.cores['neon_verde'],
                bg=self.cores['bg_frame']).pack(pady=(10, 5))
        
        self.cidade_var = tk.StringVar()
        self.entry_cidade = tk.Entry(search_frame,
                                     textvariable=self.cidade_var,
                                     font=('Segoe UI', 11),
                                     bg=self.cores['bg'],
                                     fg=self.cores['texto_claro'],
                                     insertbackground=self.cores['neon_verde'],
                                     relief=tk.FLAT)
        self.entry_cidade.pack(fill=tk.X, padx=10, pady=5)
        self.entry_cidade.bind('<Return>', lambda e: self.buscar_cidade())
        
        # Botão buscar
        btn_buscar = tk.Button(search_frame,
                              text="🔍 BUSCAR CLIMA",
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
        btn_buscar.pack(fill=tk.X, padx=10, pady=5)
        
        # Sugestões
        tk.Label(search_frame,
                text="📍 Sugestões Rápidas",
                font=('Segoe UI', 10),
                fg=self.cores['neon_amarelo'],
                bg=self.cores['bg_frame']).pack(pady=(10, 5))
        
        sugestoes_frame = tk.Frame(search_frame, bg=self.cores['bg_frame'])
        sugestoes_frame.pack(fill=tk.X, padx=10, pady=5)
        
        cidades_sugeridas = ["Carambeí", "Curitiba", "São Paulo", "Rio de Janeiro", "Brasília"]
        for cidade in cidades_sugeridas:
            btn = tk.Button(sugestoes_frame,
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
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Botões de ação
        action_frame = tk.Frame(left_frame, bg=self.cores['bg'])
        action_frame.pack(fill=tk.X, pady=10)
        
        botoes = [
            ("📊 Detalhes", self.mostrar_detalhes, self.cores['neon_roxo']),
            ("📅 7 Dias", self.mostrar_previsao_semana, self.cores['neon_laranja']),
            ("🗺️ Mapa", self.gerar_mapa, self.cores['neon_amarelo']),
            ("📈 Gráfico", self.mostrar_grafico, self.cores['neon_verde']),
            ("📄 PDF", self.exportar_pdf, self.cores['neon_rosa']),
            ("⭐ Favoritar", self.adicionar_favorito, self.cores['neon_dourado']),
            ("🗑️ Limpar", self.limpar_texto, self.cores['neon_vermelho'])
        ]
        
        for texto, comando, cor in botoes:
            btn = tk.Button(action_frame,
                           text=texto,
                           font=('Segoe UI', 9, 'bold'),
                           fg=self.cores['bg'],
                           bg=cor,
                           activebackground=self.cores['neon_azul'],
                           activeforeground=self.cores['bg'],
                           relief=tk.FLAT,
                           padx=10,
                           pady=5,
                           cursor='hand2',
                           command=comando)
            btn.pack(fill=tk.X, pady=3)
            self.aplicar_efeito_glow(btn, cor)
        
        # Histórico
        tk.Label(left_frame,
                text="📜 Histórico de Cidades",
                font=('Segoe UI', 10, 'bold'),
                fg=self.cores['neon_amarelo'],
                bg=self.cores['bg']).pack(pady=(10, 5))
        
        self.historico_listbox = tk.Listbox(left_frame,
                                           height=4,
                                           bg=self.cores['bg_frame'],
                                           fg=self.cores['texto_claro'],
                                           selectbackground=self.cores['neon_azul'],
                                           relief=tk.FLAT,
                                           font=('Segoe UI', 9))
        self.historico_listbox.pack(fill=tk.X, pady=5)
        self.historico_listbox.bind('<Double-Button-1>', self.carregar_do_historico)
        
        # Favoritos
        tk.Label(left_frame,
                text="⭐ Favoritos",
                font=('Segoe UI', 10, 'bold'),
                fg=self.cores['neon_dourado'],
                bg=self.cores['bg']).pack(pady=(5, 5))
        
        self.favoritos_listbox = tk.Listbox(left_frame,
                                           height=3,
                                           bg=self.cores['bg_frame'],
                                           fg=self.cores['texto_claro'],
                                           selectbackground=self.cores['neon_dourado'],
                                           relief=tk.FLAT,
                                           font=('Segoe UI', 9))
        self.favoritos_listbox.pack(fill=tk.X, pady=5)
        self.favoritos_listbox.bind('<Double-Button-1>', self.carregar_do_favorito)
        
        self.atualizar_historico_listbox()
        self.atualizar_favoritos_listbox()
        
        # Barra de progresso
        self.progress_bar = ttk.Progressbar(left_frame,
                                           mode='indeterminate',
                                           style='Neon.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=5)
        self.progress_bar.pack_forget()
        
        # Status
        self.status_var = tk.StringVar()
        self.status_var.set("✨ Pronto para consultar ✨")
        status_bar = tk.Label(left_frame,
                             textvariable=self.status_var,
                             font=('Segoe UI', 9, 'italic'),
                             fg=self.cores['neon_azul'],
                             bg=self.cores['bg_frame'],
                             anchor=tk.W,
                             padx=10,
                             pady=5,
                             relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Área principal
        right_frame = tk.Frame(content_frame, bg=self.cores['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de texto
        text_tab = tk.Frame(self.notebook, bg=self.cores['bg'])
        self.notebook.add(text_tab, text="📝 Clima")
        
        self.text_area = scrolledtext.ScrolledText(text_tab,
                                                  wrap=tk.WORD,
                                                  font=('Consolas', 10),
                                                  bg=self.cores['bg'],
                                                  fg=self.cores['texto_claro'],
                                                  insertbackground=self.cores['neon_verde'],
                                                  relief=tk.FLAT,
                                                  padx=15,
                                                  pady=15)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Aba de gráfico
        grafico_tab = tk.Frame(self.notebook, bg=self.cores['bg'])
        self.notebook.add(grafico_tab, text="📈 Gráficos")
        
        self.figura_frame = tk.Frame(grafico_tab, bg=self.cores['bg'])
        self.figura_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar tags
        self.configurar_tags()
    
    def configurar_tags(self):
        """Configura tags de formatação do texto"""
        tags = {
            'titulo': ('Segoe UI', 16, 'bold', self.cores['neon_azul']),
            'subtitulo': ('Segoe UI', 13, 'bold', self.cores['neon_roxo']),
            'destaque': ('Segoe UI', 12, 'bold', self.cores['neon_verde']),
            'info': ('Segoe UI', 11, self.cores['neon_rosa']),
            'separador': ('Segoe UI', 10, self.cores['neon_amarelo']),
            'erro': ('Segoe UI', 11, 'bold', self.cores['neon_vermelho']),
            'neon_laranja': ('Segoe UI', 11, self.cores['neon_laranja']),
            'neon_dourado': ('Segoe UI', 11, 'bold', self.cores['neon_dourado'])
        }
        
        for nome, (fonte, tamanho, *resto) in tags.items():
            if len(resto) == 1:
                self.text_area.tag_configure(nome, font=(fonte, tamanho), foreground=resto[0])
            elif len(resto) == 2:
                self.text_area.tag_configure(nome, font=(fonte, tamanho, resto[0]), foreground=resto[1])
    
    def aplicar_efeito_glow(self, widget, cor):
        """Aplica efeito de brilho neon nos botões"""
        widget.bind('<Enter>', lambda e: widget.config(
            bg=cor,
            fg=self.cores['bg'],
            font=('Segoe UI', 9, 'bold'),
            relief=tk.RAISED,
            bd=2
        ))
        widget.bind('<Leave>', lambda e: widget.config(
            bg=cor,
            fg=self.cores['bg'],
            font=('Segoe UI', 9, 'bold'),
            relief=tk.FLAT,
            bd=0
        ))
    
    def mostrar_splash(self):
        """Mostra tela de apresentação"""
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True)
        splash.geometry('500x350')
        splash.configure(bg='#0a0a1a')
        
        # Centralizar
        x = (self.root.winfo_screenwidth() - 500) // 2
        y = (self.root.winfo_screenheight() - 350) // 2
        splash.geometry(f'+{x}+{y}')
        
        # Conteúdo
        tk.Label(splash,
                text='🌤️',
                font=('Segoe UI', 70),
                bg='#0a0a1a').pack(pady=20)
        
        tk.Label(splash,
                text='PREVISÃO DO TEMPO NEON',
                font=('Segoe UI', 20, 'bold'),
                fg='#4ecdc4',
                bg='#0a0a1a').pack()
        
        tk.Label(splash,
                text='✨ ULTIMATE EDITION v3.0 ✨',
                font=('Segoe UI', 14, 'bold'),
                fg='#ff6b9d',
                bg='#0a0a1a').pack(pady=5)
        
        tk.Label(splash,
                text='Carregando...',
                font=('Segoe UI', 10),
                fg='#7bed9f',
                bg='#0a0a1a').pack(pady=20)
        
        # Barra de progresso
        progress = ttk.Progressbar(splash, length=300, mode='indeterminate')
        progress.pack()
        progress.start()
        
        # Fechar após 2.5 segundos
        splash.after(2500, splash.destroy)
    
    def atualizar_relogio(self):
        """Atualiza o relógio em tempo real"""
        agora = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        self.relogio_label.config(text=f"🕐 {agora}")
        self.root.after(1000, self.atualizar_relogio)
    
    def carregar_historico(self):
        """Carrega histórico de cidades"""
        try:
            if os.path.exists('historico.pkl'):
                with open('historico.pkl', 'rb') as f:
                    self.historico = pickle.load(f)
        except:
            self.historico = []
    
    def salvar_historico(self):
        """Salva histórico de cidades"""
        try:
            with open('historico.pkl', 'wb') as f:
                pickle.dump(self.historico[-20:], f)
        except:
            pass
    
    def carregar_favoritos(self):
        """Carrega lista de favoritos"""
        try:
            if os.path.exists('favoritos.pkl'):
                with open('favoritos.pkl', 'rb') as f:
                    self.favoritos = pickle.load(f)
        except:
            self.favoritos = []
    
    def salvar_favoritos(self):
        """Salva lista de favoritos"""
        try:
            with open('favoritos.pkl', 'wb') as f:
                pickle.dump(self.favoritos, f)
        except:
            pass
    
    def atualizar_historico_listbox(self):
        """Atualiza listbox de histórico"""
        self.historico_listbox.delete(0, tk.END)
        for cidade in reversed(self.historico[-10:]):
            self.historico_listbox.insert(tk.END, cidade)
    
    def atualizar_favoritos_listbox(self):
        """Atualiza listbox de favoritos"""
        self.favoritos_listbox.delete(0, tk.END)
        for cidade in self.favoritos:
            self.favoritos_listbox.insert(tk.END, cidade)
    
    def carregar_cidade_padrao(self):
        """Carrega a última cidade pesquisada"""
        if self.historico:
            self.set_cidade(self.historico[-1])
        else:
            self.set_cidade("Carambeí")
    
    def geocodificar(self, cidade):
        """Converte nome da cidade em coordenadas"""
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
        except:
            return None
    
    def buscar_dados_clima(self, lat, lon):
        """Busca dados climáticos da Open-Meteo API"""
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl,cloud_cover&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=America/Sao_Paulo&forecast_days=7"
            
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def traduzir_clima(self, weather_code):
        """Traduz código WMO para texto em português"""
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
    
    def carregar_do_historico(self, event):
        """Carrega cidade do histórico ao dar duplo clique"""
        try:
            index = self.historico_listbox.curselection()[0]
            cidade = self.historico_listbox.get(index)
            self.set_cidade(cidade)
        except:
            pass
    
    def carregar_do_favorito(self, event):
        """Carrega cidade dos favoritos ao dar duplo clique"""
        try:
            index = self.favoritos_listbox.curselection()[0]
            cidade = self.favoritos_listbox.get(index)
            self.set_cidade(cidade)
        except:
            pass
    
    def adicionar_favorito(self):
        """Adiciona cidade atual aos favoritos"""
        if hasattr(self, 'localizacao_atual') and self.localizacao_atual:
            cidade = self.localizacao_atual['nome']
            if cidade not in self.favoritos:
                self.favoritos.append(cidade)
                self.salvar_favoritos()
                self.atualizar_favoritos_listbox()
                self.status_var.set(f"⭐ {cidade} adicionado aos favoritos!")
                self.mostrar_toast(f"⭐ {cidade} favoritado!")
            else:
                self.status_var.set(f"⚠️ {cidade} já está nos favoritos!")
        else:
            self.status_var.set("⚠️ Nenhuma cidade selecionada!")
    
    def mostrar_favoritos(self):
        """Mostra lista de favoritos"""
        if self.favoritos:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "✦" * 40 + "\n", 'separador')
            self.text_area.insert(tk.END, "  ⭐ CID FAVORITAS ⭐\n", 'titulo')
            self.text_area.insert(tk.END, "✦" * 40 + "\n\n", 'separador')
            
            for i, cidade in enumerate(self.favoritos, 1):
                self.text_area.insert(tk.END, f"  {i}. {cidade}\n", 'neon_dourado')
            
            self.text_area.insert(tk.END, "\n✦" * 40 + "\n", 'separador')
            self.text_area.insert(tk.END, "  💫 Duplo clique na lista para carregar\n", 'info')
            self.status_var.set(f"⭐ {len(self.favoritos)} cidades favoritas")
        else:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "⚠️ Nenhuma cidade favorita ainda!\n", 'erro')
            self.text_area.insert(tk.END, "Clique em '⭐ Favoritar' para adicionar.\n", 'info')
    
    def mostrar_toast(self, message, duration=3000):
        """Mostra notificação toast"""
        try:
            toast = tk.Toplevel(self.root)
            toast.overrideredirect(True)
            toast.configure(bg=self.cores['bg_frame'])
            
            x = self.root.winfo_x() + self.root.winfo_width() - 350
            y = self.root.winfo_y() + self.root.winfo_height() - 100
            toast.geometry(f'300x50+{x}+{y}')
            
            frame = tk.Frame(toast, bg=self.cores['neon_azul'], bd=2)
            frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            tk.Label(frame,
                    text=f'✨ {message}',
                    font=('Segoe UI', 10),
                    fg=self.cores['texto_claro'],
                    bg=self.cores['bg_frame']).pack(expand=True)
            
            toast.after(duration, toast.destroy)
        except:
            pass
    
    def alternar_tema(self):
        """Alterna entre tema escuro e claro"""
        # Implementação simplificada
        self.modo_escuro = not self.modo_escuro
        if self.modo_escuro:
            self.status_var.set("🌙 Tema escuro ativado")
        else:
            self.status_var.set("☀️ Tema claro ativado")
    
    def mostrar_sobre(self):
        """Mostra informações sobre o programa"""
        messagebox.showinfo(
            "Sobre",
            "🌤️ PREVISÃO DO TEMPO NEON\n"
            "✨ ULTIMATE EDITION v3.0 ✨\n\n"
            "Dados fornecidos por Open-Meteo API\n"
            "Mapas com Folium\n"
            "Gráficos com Matplotlib\n"
            "PDF com ReportLab\n\n"
            "Desenvolvido com ❤️ em Python"
        )
    
    def mostrar_atalhos(self):
        """Mostra atalhos de teclado"""
        messagebox.showinfo(
            "⌨️ Atalhos de Teclado",
            "Ctrl + D - Detalhes\n"
            "Ctrl + P - Previsão 7 Dias\n"
            "Ctrl + M - Mapa\n"
            "Ctrl + G - Gráfico\n"
            "Ctrl + R - Atualizar\n"
            "Ctrl + L - Limpar\n"
            "Ctrl + F - Favoritar\n"
            "F1 - Ajuda"
        )
    
    def imprimir_relatorio(self):
        """Imprime o relatório (simulação)"""
        messagebox.showinfo("Imprimir", "Função de impressão em desenvolvimento!")
    
    def mostrar_barra_progresso(self, show=True):
        """Mostra/oculta barra de progresso"""
        if show:
            self.progress_bar.pack(fill=tk.X, pady=5)
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.pack_forget()
    
    def atualizar_clima(self):
        """Atualiza a previsão do tempo resumida"""
        self.text_area.delete(1.0, tk.END)
        cidade = self.cidade_var.get().strip()
        
        if not cidade:
            self.text_area.insert(tk.END, "⚠️ Digite o nome de uma cidade!\n", 'erro')
            self.status_var.set("⚠️ Digite o nome da cidade")
            return
        
        self.mostrar_barra_progresso(True)
        self.status_var.set(f"🌟 Buscando {cidade}... 🌟")
        self.root.update()
        
        localizacao = self.geocodificar(cidade)
        if not localizacao:
            self.mostrar_barra_progresso(False)
            self.text_area.insert(tk.END, f"❌ Cidade '{cidade}' não encontrada!\n", 'erro')
            self.text_area.insert(tk.END, "Verifique o nome e tente novamente.\n", 'info')
            self.status_var.set("❌ Cidade não encontrada")
            return
        
        self.localizacao_atual = localizacao
        
        # Adicionar ao histórico
        if cidade not in self.historico:
            self.historico.append(cidade)
            self.salvar_historico()
            self.atualizar_historico_listbox()
        
        dados_clima = self.buscar_dados_clima(localizacao['latitude'], localizacao['longitude'])
        self.mostrar_barra_progresso(False)
        
        if not dados_clima:
            self.text_area.insert(tk.END, "❌ Erro ao buscar dados climáticos!\n", 'erro')
            self.status_var.set("❌ Erro ao buscar dados")
            return
        
        current = dados_clima.get('current', {})
        weather_code = current.get('weather_code', 0)
        condicao = self.traduzir_clima(weather_code)
        
        # Header
        self.text_area.insert(tk.END, "✦" * 40 + "\n", 'separador')
        self.text_area.insert(tk.END, f"  🌸 {localizacao['nome'].upper()} - {localizacao['pais']} 🌸\n", 'titulo')
        self.text_area.insert(tk.END, f"  📍 {localizacao['regiao']}\n", 'info')
        self.text_area.insert(tk.END, "✦" * 40 + "\n\n", 'separador')
        
        # Clima atual
        self.text_area.insert(tk.END, f"  {condicao}\n\n", 'destaque')
        self.text_area.insert(tk.END, f"  🌡️  Temperatura: {current.get('temperature_2m', 'N/A')}°C\n", 'neon_laranja')
        self.text_area.insert(tk.END, f"  🌡️  Sensação: {current.get('apparent_temperature', 'N/A')}°C\n", 'info')
        self.text_area.insert(tk.END, f"  💧  Umidade: {current.get('relative_humidity_2m', 'N/A')}%\n", 'info')
        self.text_area.insert(tk.END, f"  💨  Vento: {current.get('wind_speed_10m', 'N/A')} km/h\n", 'info')
        self.text_area.insert(tk.END, f"  🌧️  Precipitação: {current.get('precipitation', 'N/A')} mm\n", 'info')
        self.text_area.insert(tk.END, f"  ☁️  Nuvens: {current.get('cloud_cover', 'N/A')}%\n\n", 'info')
        
        self.text_area.insert(tk.END, "✦" * 40 + "\n", 'separador')
        self.text_area.insert(tk.END, "  💫 Ações disponíveis:\n", 'info')
        self.text_area.insert(tk.END, "  📊 Detalhes  |  📅 7 Dias  |  🗺️ Mapa\n", 'neon_laranja')
        self.text_area.insert(tk.END, "  📈 Gráfico  |  📄 PDF  |  ⭐ Favoritar\n", 'neon_laranja')
        self.text_area.insert(tk.END, "✦" * 40 + "\n", 'separador')
        
        self.status_var.set(f"✨ {localizacao['nome']} atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ✨")
        self.mostrar_toast(f"Clima de {localizacao['nome']} atualizado!")
    
    def mostrar_detalhes(self):
        """Mostra os detalhes completos"""
        if not hasattr(self, 'localizacao_atual') or not self.localizacao_atual:
            self.atualizar_clima()
            return
        
        local = self.localizacao_atual
        cidade = local['nome']
        
        self.mostrar_barra_progresso(True)
        self.status_var.set(f"🌟 Carregando detalhes para {cidade}... 🌟")
        self.root.update()
        
        dados_clima = self.buscar_dados_clima(local['latitude'], local['longitude'])
        self.mostrar_barra_progresso(False)
        
        if not dados_clima:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "❌ Erro ao buscar dados climáticos!\n", 'erro')
            return
        
        self.text_area.delete(1.0, tk.END)
        current = dados_clima.get('current', {})
        weather_code = current.get('weather_code', 0)
        condicao = self.traduzir_clima(weather_code)
        
        self.text_area.insert(tk.END, "✦" * 50 + "\n", 'separador')
        self.text_area.insert(tk.END, f"  🌸 DETALHES - {cidade.upper()} 🌸\n", 'titulo')
        self.text_area.insert(tk.END, "✦" * 50 + "\n\n", 'separador')
        
        self.text_area.insert(tk.END, "📍 LOCALIZAÇÃO\n", 'subtitulo')
        self.text_area.insert(tk.END, f"  Cidade: {local['nome']}\n", 'info')
        self.text_area.insert(tk.END, f"  Região: {local['regiao']}\n", 'info')
        self.text_area.insert(tk.END, f"  País: {local['pais']}\n", 'info')
        self.text_area.insert(tk.END, f"  Coordenadas: {local['latitude']}°, {local['longitude']}°\n\n", 'info')
        
        self.text_area.insert(tk.END, "🌡️ CONDIÇÕES ATUAIS\n", 'subtitulo')
        self.text_area.insert(tk.END, f"  {condicao}\n", 'destaque')
        self.text_area.insert(tk.END, f"  🌡️  Temperatura: {current.get('temperature_2m', 'N/A')}°C\n", 'neon_laranja')
        self.text_area.insert(tk.END, f"  🌡️  Sensação térmica: {current.get('apparent_temperature', 'N/A')}°C\n", 'info')
        self.text_area.insert(tk.END, f"  💧  Umidade: {current.get('relative_humidity_2m', 'N/A')}%\n", 'info')
        self.text_area.insert(tk.END, f"  💨  Vento: {current.get('wind_speed_10m', 'N/A')} km/h\n", 'info')
        self.text_area.insert(tk.END, f"  🧭  Direção: {current.get('wind_direction_10m', 'N/A')}°\n", 'info')
        self.text_area.insert(tk.END, f"  🌧️  Precipitação: {current.get('precipitation', 'N/A')} mm\n", 'info')
        self.text_area.insert(tk.END, f"  📊  Pressão: {current.get('pressure_msl', 'N/A')} hPa\n", 'info')
        self.text_area.insert(tk.END, f"  ☁️  Nebulosidade: {current.get('cloud_cover', 'N/A')}%\n\n", 'info')
        
        self.text_area.insert(tk.END, "✦" * 50 + "\n", 'separador')
        self.text_area.insert(tk.END, "💫 Dados fornecidos por Open-Meteo\n", 'info')
        self.status_var.set(f"✨ Detalhes de {cidade} atualizados ✨")
    
    def mostrar_previsao_semana(self):
        """Mostra a previsão para 7 dias"""
        if not hasattr(self, 'localizacao_atual') or not self.localizacao_atual:
            self.atualizar_clima()
            return
        
        local = self.localizacao_atual
        cidade = local['nome']
        
        self.mostrar_barra_progresso(True)
        self.status_var.set(f"🌟 Carregando previsão para {cidade}... 🌟")
        self.root.update()
        
        dados_clima = self.buscar_dados_clima(local['latitude'], local['longitude'])
        self.mostrar_barra_progresso(False)
        
        if not dados_clima:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "❌ Erro ao buscar dados climáticos!\n", 'erro')
            return
        
        self.text_area.delete(1.0, tk.END)
        daily = dados_clima.get('daily', {})
        
        self.text_area.insert(tk.END, "✦" * 55 + "\n", 'separador')
        self.text_area.insert(tk.END, f"  📅 PREVISÃO 7 DIAS - {cidade.upper()} 📅\n", 'titulo')
        self.text_area.insert(tk.END, "✦" * 55 + "\n\n", 'separador')
        
        datas = daily.get('time', [])
        temp_max = daily.get('temperature_2m_max', [])
        temp_min = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        weather_codes = daily.get('weather_code', [])
        
        dias_semana = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO', 'DOMINGO']
        
        for i in range(min(7, len(datas))):
            data_obj = datetime.strptime(datas[i], '%Y-%m-%d')
            nome_dia = dias_semana[data_obj.weekday()]
            data_formatada = data_obj.strftime('%d/%m')
            
            condicao = self.traduzir_clima(weather_codes[i] if i < len(weather_codes) else 0)
            
            self.text_area.insert(tk.END, f"  📆 {nome_dia} - {data_formatada}\n", 'destaque')
            self.text_area.insert(tk.END, f"     {condicao}\n", 'info')
            self.text_area.insert(tk.END, f"     🔥 Máx: {temp_max[i] if i < len(temp_max) else 'N/A'}°C", 'neon_laranja')
            self.text_area.insert(tk.END, f"  ❄️ Mín: {temp_min[i] if i < len(temp_min) else 'N/A'}°C\n", 'neon_laranja')
            self.text_area.insert(tk.END, f"     🌧️  Precipitação: {precip[i] if i < len(precip) else 'N/A'} mm\n\n", 'info')
        
        self.text_area.insert(tk.END, "✦" * 55 + "\n", 'separador')
        self.text_area.insert(tk.END, "💫 Dados fornecidos por Open-Meteo\n", 'info')
        self.status_var.set(f"✨ Previsão de {cidade} atualizada ✨")
    
    def mostrar_grafico(self):
        """Mostra gráfico de temperatura e precipitação"""
        if not hasattr(self, 'localizacao_atual') or not self.localizacao_atual:
            self.atualizar_clima()
            return
        
        local = self.localizacao_atual
        cidade = local['nome']
        
        self.mostrar_barra_progresso(True)
        self.status_var.set(f"🌟 Gerando gráfico para {cidade}... 🌟")
        self.root.update()
        
        dados_clima = self.buscar_dados_clima(local['latitude'], local['longitude'])
        self.mostrar_barra_progresso(False)
        
        if not dados_clima:
            messagebox.showerror("Erro", "Não foi possível buscar os dados climáticos!")
            return
        
        # Mudar para a aba de gráficos
        self.notebook.select(1)
        
        # Limpar frame anterior
        for widget in self.figura_frame.winfo_children():
            widget.destroy()
        
        # Criar figura com dois subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='#0a0a1a')
        
        daily = dados_clima.get('daily', {})
        datas = [datetime.strptime(d, '%Y-%m-%d') for d in daily.get('time', [])]
        temp_max = daily.get('temperature_2m_max', [])
        temp_min = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        
        # Gráfico de temperatura
        ax1.plot(datas, temp_max, color='#ff6b9d', marker='o', linewidth=2, label='Máxima')
        ax1.plot(datas, temp_min, color='#4ecdc4', marker='s', linewidth=2, label='Mínima')
        ax1.fill_between(datas, temp_min, temp_max, alpha=0.3, color='#a29bfe')
        ax1.set_title(f'Temperatura - {cidade}', color='#f0f0f0', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Temperatura (°C)', color='#f0f0f0')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#1a1a3e')
        ax1.tick_params(colors='#f0f0f0')
        
        # Gráfico de precipitação
        ax2.bar(datas, precip, color='#7bed9f', alpha=0.7, label='Precipitação')
        ax2.set_title(f'Precipitação - {cidade}', color='#f0f0f0', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Precipitação (mm)', color='#f0f0f0')
        ax2.set_xlabel('Data', color='#f0f0f0')
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#1a1a3e')
        ax2.tick_params(colors='#f0f0f0')
        
        # Formatando datas
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Mostrar no Tkinter
        canvas = FigureCanvasTkAgg(fig, self.figura_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.status_var.set(f"✨ Gráfico de {cidade} gerado com sucesso! ✨")
        self.mostrar_toast(f"📈 Gráfico de {cidade} gerado!")
    
    def gerar_mapa(self):
        """Gera e abre um mapa interativo"""
        if not hasattr(self, 'localizacao_atual') or not self.localizacao_atual:
            self.atualizar_clima()
            return
        
        local = self.localizacao_atual
        cidade = local['nome']
        
        self.mostrar_barra_progresso(True)
        self.status_var.set(f"🗺️ Gerando mapa para {cidade}...")
        self.root.update()
        
        try:
            mapa = folium.Map(
                location=[local['latitude'], local['longitude']],
                zoom_start=13,
                tiles='CartoDB dark_matter',
                control_scale=True
            )
            
            folium.Marker(
                [local['latitude'], local['longitude']],
                popup=f'<b>{cidade}</b><br>{local["pais"]}',
                tooltip=f'Clique para detalhes de {cidade}',
                icon=folium.Icon(color='pink', icon='cloud', prefix='fa')
            ).add_to(mapa)
            
            folium.Circle(
                [local['latitude'], local['longitude']],
                radius=1000,
                color='#ff6b9d',
                fill=True,
                fill_color='#ff6b9d',
                fill_opacity=0.2,
                popup=f'Área de {cidade}'
            ).add_to(mapa)
            
            mapa_path = os.path.join(os.getcwd(), f'mapa_{cidade}.html')
            mapa.save(mapa_path)
            webbrowser.open(f'file://{mapa_path}')
            
            self.mostrar_barra_progresso(False)
            self.status_var.set(f"🗺️ Mapa de {cidade} aberto no navegador")
            self.mostrar_toast(f"🗺️ Mapa de {cidade} gerado!")
            
        except Exception as e:
            self.mostrar_barra_progresso(False)
            messagebox.showerror("Erro", f"Erro ao gerar mapa: {str(e)}")
            self.status_var.set("❌ Erro ao gerar mapa")
    
    def exportar_pdf(self):
        """Exporta o relatório do clima para PDF"""
        if not hasattr(self, 'localizacao_atual') or not self.localizacao_atual:
            self.atualizar_clima()
            return
        
        local = self.localizacao_atual
        cidade = local['nome']
        
        self.mostrar_barra_progresso(True)
        self.status_var.set(f"📄 Gerando PDF para {cidade}...")
        self.root.update()
        
        dados_clima = self.buscar_dados_clima(local['latitude'], local['longitude'])
        
        if not dados_clima:
            self.mostrar_barra_progresso(False)
            messagebox.showerror("Erro", "Não foi possível buscar os dados climáticos!")
            return
        
        try:
            pdf_path = f"relatorio_{cidade}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#4ecdc4'),
                alignment=1,
                spaceAfter=30
            )
            story.append(Paragraph(f"🌤️ RELATÓRIO CLIMÁTICO - {cidade.upper()}", title_style))
            story.append(Spacer(1, 0.25*inch))
            
            # Data
            normal_style = styles['Normal']
            story.append(Paragraph(f"Data do relatório: {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal_style))
            story.append(Spacer(1, 0.25*inch))
            
            # Dados atuais
            current = dados_clima.get('current', {})
            weather_code = current.get('weather_code', 0)
            condicao = self.traduzir_clima(weather_code)
            
            story.append(Paragraph("📍 LOCALIZAÇÃO", styles['Heading2']))
            story.append(Paragraph(f"Cidade: {local['nome']}", normal_style))
            story.append(Paragraph(f"Região: {local['regiao']}", normal_style))
            story.append(Paragraph(f"País: {local['pais']}", normal_style))
            story.append(Spacer(1, 0.2*inch))
            
            story.append(Paragraph("🌡️ CONDIÇÕES ATUAIS", styles['Heading2']))
            story.append(Paragraph(f"Condição: {condicao}", normal_style))
            story.append(Paragraph(f"Temperatura: {current.get('temperature_2m', 'N/A')}°C", normal_style))
            story.append(Paragraph(f"Sensação térmica: {current.get('apparent_temperature', 'N/A')}°C", normal_style))
            story.append(Paragraph(f"Umidade: {current.get('relative_humidity_2m', 'N/A')}%", normal_style))
            story.append(Paragraph(f"Vento: {current.get('wind_speed_10m', 'N/A')} km/h", normal_style))
            story.append(Paragraph(f"Precipitação: {current.get('precipitation', 'N/A')} mm", normal_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Previsão 7 dias
            story.append(Paragraph("📅 PREVISÃO 7 DIAS", styles['Heading2']))
            
            daily = dados_clima.get('daily', {})
            datas = daily.get('time', [])
            temp_max = daily.get('temperature_2m_max', [])
            temp_min = daily.get('temperature_2m_min', [])
            precip = daily.get('precipitation_sum', [])
            weather_codes = daily.get('weather_code', [])
            
            dias_semana = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO', 'DOMINGO']
            
            for i in range(min(7, len(datas))):
                data_obj = datetime.strptime(datas[i], '%Y-%m-%d')
                nome_dia = dias_semana[data_obj.weekday()]
                cond = self.traduzir_clima(weather_codes[i] if i < len(weather_codes) else 0)
                
                story.append(Paragraph(f"{nome_dia} - {data_obj.strftime('%d/%m/%Y')}", styles['Heading3']))
                story.append(Paragraph(f"Condição: {cond}", normal_style))
                story.append(Paragraph(f"Máx: {temp_max[i] if i < len(temp_max) else 'N/A'}°C | Mín: {temp_min[i] if i < len(temp_min) else 'N/A'}°C", normal_style))
                story.append(Paragraph(f"Precipitação: {precip[i] if i < len(precip) else 'N/A'} mm", normal_style))
                story.append(Spacer(1, 0.1*inch))
            
            # Rodapé
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph("💫 Dados fornecidos por Open-Meteo API", styles['Italic']))
            
            # Gerar PDF
            doc.build(story)
            
            self.mostrar_barra_progresso(False)
            messagebox.showinfo("Sucesso", f"PDF gerado com sucesso!\nArquivo: {pdf_path}")
            self.status_var.set(f"📄 PDF gerado: {pdf_path}")
            self.mostrar_toast(f"📄 PDF de {cidade} gerado!")
            
            # Abrir o PDF
            os.startfile(pdf_path) if os.name == 'nt' else webbrowser.open(pdf_path)
            
        except Exception as e:
            self.mostrar_barra_progresso(False)
            messagebox.showerror("Erro", f"Erro ao gerar PDF: {str(e)}")
            self.status_var.set("❌ Erro ao gerar PDF")
    
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