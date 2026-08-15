import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.clima_service import ClimaService
from core.exceptions import ClimaException
from core.models import PrevisaoCompleta
from gui.styles import NeonTheme
from gui.widgets.search_panel import SearchPanel
from gui.widgets.weather_display import WeatherDisplay
from utils.logger import log


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🌤️ Previsão do Tempo Neon")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        self.clima_service = ClimaService()
        self.previsao_atual: Optional[PrevisaoCompleta] = None
        
        # Inicializar UI
        self._setup_ui()
        self._setup_bindings()
        
        # Carregar cidade padrão
        self.carregar_cidade("Carambeí")
    
    def _setup_ui(self):
        """Configura a interface"""
        theme = NeonTheme()
        
        # Container principal
        self.main_container = tk.Frame(self.root, bg=theme.bg)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Barra superior
        self.top_bar = self._criar_top_bar(theme)
        self.top_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Área de conteúdo
        self.content_frame = tk.Frame(self.main_container, bg=theme.bg)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Painel de busca (esquerda)
        self.search_panel = SearchPanel(
            self.content_frame,
            theme=theme,
            on_search=self.carregar_cidade
        )
        self.search_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Área principal (direita)
        self.right_frame = tk.Frame(self.content_frame, bg=theme.bg)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook para abas
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.weather_display = WeatherDisplay(
            self.notebook,
            theme=theme,
            clima_service=self.clima_service,
            mode="current"
        )
        self.notebook.add(self.weather_display, text="🌤️ Hoje")

        self.forecast_display = WeatherDisplay(
            self.notebook,
            theme=theme,
            clima_service=self.clima_service,
            mode="forecast"
        )
        self.notebook.add(self.forecast_display, text="📅 7 dias")
        
        # Status bar
        self.status_bar = tk.Label(
            self.main_container,
            text="✨ Pronto para consultar ✨",
            font=('Segoe UI', 9, 'italic'),
            fg=theme.neon_azul,
            bg=theme.bg_frame,
            anchor=tk.W,
            padx=10,
            pady=5,
            relief=tk.SUNKEN
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def _criar_top_bar(self, theme):
        """Cria a barra superior"""
        top_bar = tk.Frame(self.main_container, bg=theme.bg_frame, height=60)
        top_bar.pack_propagate(False)
        
        # Título
        titulo = tk.Label(
            top_bar,
            text="🌤️ PREVISÃO DO TEMPO NEON",
            font=('Segoe UI', 18, 'bold'),
            fg=theme.neon_azul,
            bg=theme.bg_frame
        )
        titulo.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Versão
        versao = tk.Label(
            top_bar,
            text="v4.0 PRO",
            font=('Segoe UI', 9, 'bold'),
            fg=theme.neon_rosa,
            bg=theme.bg_frame
        )
        versao.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Relógio
        self.relogio_label = tk.Label(
            top_bar,
            font=('Segoe UI', 14, 'bold'),
            fg=theme.neon_verde,
            bg=theme.bg_frame
        )
        self.relogio_label.pack(side=tk.RIGHT, padx=20, pady=10)
        self._atualizar_relogio()
        
        return top_bar
    
    def _atualizar_relogio(self):
        """Atualiza o relógio"""
        from datetime import datetime
        agora = datetime.now().strftime("%H:%M:%S - %d/%m/%Y")
        self.relogio_label.config(text=f"🕐 {agora}")
        self.root.after(1000, self._atualizar_relogio)
    
    def _setup_bindings(self):
        """Configura atalhos de teclado"""
        self.root.bind('<Control-r>', lambda e: self.carregar_cidade(self.search_panel.get_cidade()))
        self.root.bind('<Control-1>', lambda e: self.notebook.select(0))
        self.root.bind('<Control-2>', lambda e: self.notebook.select(1))
    
    def carregar_cidade(self, cidade: str):
        """Carrega dados de uma cidade (em thread separada)"""
        if not cidade or not cidade.strip():
            self._atualizar_status("⚠️ Digite o nome de uma cidade", erro=True)
            return
        
        self._atualizar_status(f"🌟 Buscando {cidade}...")
        self.search_panel.mostrar_carregando(True)
        
        # Executar em thread separada
        thread = threading.Thread(
            target=self._carregar_cidade_thread,
            args=(cidade.strip(),),
            daemon=True
        )
        thread.start()
    
    def _carregar_cidade_thread(self, cidade: str):
        """Thread para carregar cidade"""
        try:
            previsao = self.clima_service.buscar_previsao(cidade)
            
            # Atualizar UI na thread principal
            self.root.after(0, self._atualizar_ui, previsao)
            
        except ClimaException as e:
            self.root.after(0, self._mostrar_erro, str(e))
        except Exception as e:
            log.error(f"Erro inesperado: {e}")
            self.root.after(0, self._mostrar_erro, f"Erro inesperado: {str(e)}")
    
    def _atualizar_ui(self, previsao: PrevisaoCompleta):
        """Atualiza a UI com os dados"""
        self.search_panel.mostrar_carregando(False)
        
        if previsao:
            self.previsao_atual = previsao
            self.weather_display.atualizar(previsao)
            self.forecast_display.atualizar(previsao)
            self._atualizar_status(f"✨ {previsao.atual.coordenadas.cidade} atualizado!")
        else:
            self._mostrar_erro("Erro ao buscar dados")
    
    def _mostrar_erro(self, mensagem: str):
        """Mostra mensagem de erro"""
        self.search_panel.mostrar_carregando(False)
        self._atualizar_status(f"❌ {mensagem}", erro=True)
        self.weather_display.mostrar_erro(mensagem)
    
    def _atualizar_status(self, mensagem: str, erro: bool = False):
        """Atualiza a barra de status"""
        self.status_bar.config(
            text=mensagem,
            fg='#ff4757' if erro else self.status_bar.cget('fg')
        )
        self.root.update()