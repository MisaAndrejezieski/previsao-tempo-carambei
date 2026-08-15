import json
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, ttk

import requests


class PrevisaoTempoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Previsão do Tempo - Carambeí")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        
        # Cores neon pasteis
        self.cores = {
            'bg': '#1a1a2e',           # Fundo escuro
            'bg_frame': '#16213e',      # Fundo frames
            'neon_rosa': '#ff6b9d',     # Rosa neon
            'neon_azul': '#4ecdc4',     # Azul neon
            'neon_verde': '#7bed9f',    # Verde neon
            'neon_roxo': '#a29bfe',     # Roxo neon
            'neon_amarelo': '#ffeaa7',  # Amarelo neon
            'neon_laranja': '#fd79a8',  # Laranja neon
            'texto_claro': '#dfe6e9',   # Texto claro
            'texto_escuro': '#2d3436',  # Texto escuro
            'status_bg': '#2d2d44',     # Fundo status
        }
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilizar botões
        style.configure('Neon.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       foreground=self.cores['texto_claro'],
                       background=self.cores['neon_rosa'],
                       padding=10)
        
        # Configurar fundo da janela
        self.root.configure(bg=self.cores['bg'])
        
        # Frame principal
        main_frame = tk.Frame(root, bg=self.cores['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título com efeito neon
        titulo_frame = tk.Frame(main_frame, bg=self.cores['bg'])
        titulo_frame.grid(row=0, column=0, pady=(0, 15))
        
        titulo = tk.Label(titulo_frame, 
                         text="🌤️ PREVISÃO DO TEMPO - CARAMBEÍ 🌤️",
                         font=('Segoe UI', 18, 'bold'),
                         fg=self.cores['neon_azul'],
                         bg=self.cores['bg'])
        titulo.pack()
        
        # Subtítulo com efeito neon
        subtitulo = tk.Label(titulo_frame,
                            text="✦ Clima em tempo real ✦",
                            font=('Segoe UI', 11, 'italic'),
                            fg=self.cores['neon_roxo'],
                            bg=self.cores['bg'])
        subtitulo.pack()
        
        # Frame para botões com borda neon
        button_frame = tk.Frame(main_frame, bg=self.cores['bg_frame'], 
                               relief=tk.RAISED, bd=2)
        button_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Botões estilizados
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
        
        self.btn_limpar = tk.Button(button_frame,
                                   text="🗑️ Limpar",
                                   font=('Segoe UI', 10, 'bold'),
                                   fg=self.cores['bg'],
                                   bg=self.cores['neon_laranja'],
                                   activebackground=self.cores['neon_rosa'],
                                   activeforeground=self.cores['bg'],
                                   relief=tk.FLAT,
                                   padx=15,
                                   pady=8,
                                   cursor='hand2',
                                   command=self.limpar_texto)
        self.btn_limpar.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Status bar neon
        status_frame = tk.Frame(main_frame, bg=self.cores['bg_frame'])
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
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
        
        # Área de texto com tema neon
        text_frame = tk.Frame(main_frame, bg=self.cores['bg_frame'], 
                            relief=tk.RAISED, bd=2)
        text_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.text_area = scrolledtext.ScrolledText(text_frame,
                                                  wrap=tk.WORD,
                                                  width=80,
                                                  height=25,
                                                  font=('Consolas', 10),
                                                  bg=self.cores['bg'],
                                                  fg=self.cores['texto_claro'],
                                                  insertbackground=self.cores['neon_verde'],
                                                  relief=tk.FLAT,
                                                  padx=10,
                                                  pady=10)
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar tags para formatação neon
        self.text_area.tag_configure('titulo', 
                                    font=('Segoe UI', 13, 'bold'),
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
                                    foreground='#ff4757',
                                    font=('Segoe UI', 10, 'bold'))
        self.text_area.tag_configure('neon_laranja',
                                    foreground=self.cores['neon_laranja'])
        
        # Carregar dados iniciais
        self.atualizar_clima()
    
    def atualizar_clima(self):
        """Atualiza a previsão do tempo resumida"""
        self.text_area.delete(1.0, tk.END)
        self.status_var.set("🌟 Consultando clima... 🌟")
        self.root.update()
        
        try:
            url_resumo = "https://wttr.in/Carambei?format=3&lang=pt"
            response = requests.get(url_resumo, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                resumo = response.text.strip()
                
                # Cabeçalho com neon
                self.text_area.insert(tk.END, "✦" * 30 + "\n", 'separador')
                self.text_area.insert(tk.END, "  🌸 CLIMA ATUAL - CARAMBEÍ 🌸\n", 'titulo')
                self.text_area.insert(tk.END, "✦" * 30 + "\n\n", 'separador')
                self.text_area.insert(tk.END, f"  {resumo}\n\n", 'destaque')
                self.text_area.insert(tk.END, "✦" * 30 + "\n", 'separador')
                self.text_area.insert(tk.END, "  💫 Para detalhes completos, clique em\n", 'info')
                self.text_area.insert(tk.END, "  '📊 Detalhes Completos'\n", 'neon_laranja')
                self.text_area.insert(tk.END, "✦" * 30 + "\n", 'separador')
                
                self.status_var.set(f"✨ Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ✨")
            else:
                self.text_area.insert(tk.END, "❌ Erro ao consultar o clima.\n", 'erro')
                self.status_var.set("❌ Erro na consulta")
                
        except requests.exceptions.RequestException as e:
            self.text_area.insert(tk.END, f"⚠️ Erro de conexão: {str(e)}\n", 'erro')
            self.text_area.insert(tk.END, "🔌 Verifique sua conexão com a internet.\n", 'erro')
            self.status_var.set("⚠️ Erro de conexão")
        except Exception as e:
            self.text_area.insert(tk.END, f"💥 Erro inesperado: {str(e)}\n", 'erro')
            self.status_var.set("💥 Erro inesperado")
    
    def mostrar_detalhes(self):
        """Mostra os detalhes completos da previsão"""
        self.status_var.set("🌟 Carregando detalhes completos... 🌟")
        self.root.update()
        
        try:
            url_json = "https://wttr.in/Carambei?format=j1&lang=pt"
            response = requests.get(url_json, timeout=15)
            
            if response.status_code == 200:
                dados = response.json()
                self.text_area.delete(1.0, tk.END)
                self.mostrar_detalhes_estruturados(dados)
                self.status_var.set(f"✨ Detalhes atualizados: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ✨")
            else:
                # Fallback para formato texto
                self.text_area.delete(1.0, tk.END)
                url_texto = "https://wttr.in/Carambei?lang=pt"
                response = requests.get(url_texto, timeout=10)
                response.encoding = 'utf-8'
                self.text_area.insert(tk.END, response.text, 'info')
                self.status_var.set("✨ Detalhes carregados (modo texto) ✨")
                
        except requests.exceptions.RequestException as e:
            self.text_area.insert(tk.END, f"⚠️ Erro de conexão: {str(e)}\n", 'erro')
            self.status_var.set("⚠️ Erro de conexão")
        except Exception as e:
            self.text_area.insert(tk.END, f"💥 Erro inesperado: {str(e)}\n", 'erro')
            self.status_var.set("💥 Erro inesperado")
    
    def mostrar_detalhes_estruturados(self, dados):
        """Mostra os detalhes em formato estruturado com estilo neon"""
        try:
            atual = dados.get('current_condition', [{}])[0]
            local = dados.get('nearest_area', [{}])[0]
            
            # Cabeçalho neon
            self.text_area.insert(tk.END, "✦" * 40 + "\n", 'separador')
            self.text_area.insert(tk.END, "  🌸 DETALHES COMPLETOS - CARAMBEÍ 🌸\n", 'titulo')
            self.text_area.insert(tk.END, "✦" * 40 + "\n\n", 'separador')
            
            # Localização
            self.text_area.insert(tk.END, "📍 LOCALIZAÇÃO\n", 'subtitulo')
            self.text_area.insert(tk.END, f"  Cidade: {local.get('areaName', [{}])[0].get('value', 'N/A')}\n", 'info')
            self.text_area.insert(tk.END, f"  Região: {local.get('region', [{}])[0].get('value', 'N/A')}\n", 'info')
            self.text_area.insert(tk.END, f"  País: {local.get('country', [{}])[0].get('value', 'N/A')}\n\n", 'info')
            
            # Condições atuais
            self.text_area.insert(tk.END, "🌡️ CONDIÇÕES ATUAIS\n", 'subtitulo')
            self.text_area.insert(tk.END, f"  🌡️  Temperatura: {atual.get('temp_C', 'N/A')}°C\n", 'destaque')
            self.text_area.insert(tk.END, f"  🌡️  Sensação: {atual.get('FeelsLikeC', 'N/A')}°C\n", 'info')
            self.text_area.insert(tk.END, f"  ☁️  Condição: {atual.get('weatherDesc', [{}])[0].get('value', 'N/A')}\n", 'info')
            self.text_area.insert(tk.END, f"  💧  Umidade: {atual.get('humidity', 'N/A')}%\n", 'neon_laranja')
            self.text_area.insert(tk.END, f"  💨  Vento: {atual.get('windspeedKmph', 'N/A')} km/h\n", 'info')
            self.text_area.insert(tk.END, f"  🧭  Direção: {atual.get('winddir16Point', 'N/A')}\n", 'info')
            self.text_area.insert(tk.END, f"  📊  Pressão: {atual.get('pressure', 'N/A')} mb\n", 'info')
            self.text_area.insert(tk.END, f"  👁️  Visibilidade: {atual.get('visibility', 'N/A')} km\n", 'info')
            self.text_area.insert(tk.END, f"  ☀️  UV Index: {atual.get('uvIndex', 'N/A')}\n", 'neon_roxo')
            self.text_area.insert(tk.END, f"  ☁️  Nuvens: {atual.get('cloudcover', 'N/A')}%\n\n", 'info')
            
            # Previsão
            previsao = dados.get('weather', [])
            if previsao:
                self.text_area.insert(tk.END, "📅 PREVISÃO PARA OS PRÓXIMOS DIAS\n", 'subtitulo')
                self.text_area.insert(tk.END, "─" * 40 + "\n", 'separador')
                
                for dia in previsao[:3]:
                    data = dia.get('date', 'N/A')
                    max_temp = dia.get('maxtempC', 'N/A')
                    min_temp = dia.get('mintempC', 'N/A')
                    condicao = dia.get('hourly', [{}])[0].get('weatherDesc', [{}])[0].get('value', 'N/A')
                    
                    self.text_area.insert(tk.END, f"  📆 {data}\n", 'destaque')
                    self.text_area.insert(tk.END, f"     {condicao}\n", 'info')
                    self.text_area.insert(tk.END, f"     🔥 Máx: {max_temp}°C  ❄️ Mín: {min_temp}°C\n\n", 'neon_laranja')
            
            self.text_area.insert(tk.END, "✦" * 40 + "\n", 'separador')
            self.text_area.insert(tk.END, "💫 Dados fornecidos por wttr.in\n", 'info')
            
        except Exception as e:
            self.text_area.insert(tk.END, f"💥 Erro ao processar dados: {str(e)}\n", 'erro')
    
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