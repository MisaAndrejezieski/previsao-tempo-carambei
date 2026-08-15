import json
import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext, ttk

import requests


class PrevisaoTempoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Previsão do Tempo - Carambeí")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="🌤️ PREVISÃO DO TEMPO - CARAMBEÍ 🌤️", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, pady=10)
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Botões
        self.btn_atualizar = ttk.Button(button_frame, text="🔄 Atualizar Clima", 
                                       command=self.atualizar_clima)
        self.btn_atualizar.pack(side=tk.LEFT, padx=5)
        
        self.btn_detalhes = ttk.Button(button_frame, text="📊 Ver Detalhes Completos", 
                                      command=self.mostrar_detalhes)
        self.btn_detalhes.pack(side=tk.LEFT, padx=5)
        
        self.btn_limpar = ttk.Button(button_frame, text="🗑️ Limpar", 
                                    command=self.limpar_texto)
        self.btn_limpar.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para consultar")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                                   relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Área de texto com scroll
        self.text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, 
                                                  width=80, height=25,
                                                  font=('Courier New', 10))
        self.text_area.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para formatação
        self.text_area.tag_configure('titulo', font=('Arial', 12, 'bold'), foreground='blue')
        self.text_area.tag_configure('subtitulo', font=('Arial', 11, 'bold'))
        self.text_area.tag_configure('destaque', font=('Arial', 10, 'bold'), foreground='darkgreen')
        self.text_area.tag_configure('info', foreground='darkblue')
        self.text_area.tag_configure('separador', foreground='gray')
        self.text_area.tag_configure('erro', foreground='red')
        
        # Carregar dados iniciais
        self.atualizar_clima()
    
    def atualizar_clima(self):
        """Atualiza a previsão do tempo resumida"""
        self.text_area.delete(1.0, tk.END)
        self.status_var.set("Consultando clima...")
        self.root.update()
        
        try:
            # Resumo rápido (formato 3)
            url_resumo = "https://wttr.in/Carambei?format=3&lang=pt"
            response = requests.get(url_resumo, timeout=10)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                resumo = response.text.strip()
                self.text_area.insert(tk.END, "=" * 45 + "\n")
                self.text_area.insert(tk.END, "  CLIMA ATUAL - CARAMBEÍ (via wttr.in)\n", 'titulo')
                self.text_area.insert(tk.END, "=" * 45 + "\n\n")
                self.text_area.insert(tk.END, resumo + "\n\n", 'destaque')
                self.text_area.insert(tk.END, "=" * 45 + "\n")
                self.text_area.insert(tk.END, "  Para detalhes completos, clique em\n", 'info')
                self.text_area.insert(tk.END, "  'Ver Detalhes Completos'\n", 'info')
                self.text_area.insert(tk.END, "=" * 45 + "\n")
                
                self.status_var.set(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                self.text_area.insert(tk.END, "Erro ao consultar o clima. Código: " + 
                                     str(response.status_code) + "\n", 'erro')
                self.status_var.set("Erro na consulta")
                
        except requests.exceptions.RequestException as e:
            self.text_area.insert(tk.END, f"Erro de conexão: {str(e)}\n", 'erro')
            self.text_area.insert(tk.END, "Verifique sua conexão com a internet.\n", 'erro')
            self.status_var.set("Erro de conexão")
        except Exception as e:
            self.text_area.insert(tk.END, f"Erro inesperado: {str(e)}\n", 'erro')
            self.status_var.set("Erro inesperado")
    
    def mostrar_detalhes(self):
        """Mostra os detalhes completos da previsão"""
        # Verificar se já tem conteúdo
        if not self.text_area.get(1.0, tk.END).strip():
            self.text_area.insert(tk.END, "Carregando detalhes...\n", 'info')
            self.root.update()
        
        self.status_var.set("Carregando detalhes completos...")
        self.root.update()
        
        try:
            # Detalhes completos
            url_detalhes = "https://wttr.in/Carambei?lang=pt&format=%l:+%c+%t+%w+%h+%p+%P+%u"
            response = requests.get(url_detalhes, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                # Limpar e mostrar detalhes
                self.text_area.delete(1.0, tk.END)
                
                self.text_area.insert(tk.END, "=" * 60 + "\n")
                self.text_area.insert(tk.END, "  DETALHES COMPLETOS - PREVISÃO DO TEMPO\n", 'titulo')
                self.text_area.insert(tk.END, "=" * 60 + "\n\n")
                
                # Tentar obter dados em formato mais estruturado
                try:
                    url_json = "https://wttr.in/Carambei?format=j1&lang=pt"
                    response_json = requests.get(url_json, timeout=10)
                    if response_json.status_code == 200:
                        dados = response_json.json()
                        self.mostrar_detalhes_estruturados(dados)
                    else:
                        # Fallback para formato texto
                        self.text_area.insert(tk.END, response.text + "\n", 'info')
                except:
                    # Fallback para formato texto simples
                    self.text_area.insert(tk.END, response.text + "\n", 'info')
                
                self.status_var.set(f"Detalhes atualizados: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                self.text_area.insert(tk.END, "Erro ao carregar detalhes.\n", 'erro')
                self.status_var.set("Erro ao carregar detalhes")
                
        except requests.exceptions.RequestException as e:
            self.text_area.insert(tk.END, f"Erro de conexão: {str(e)}\n", 'erro')
            self.status_var.set("Erro de conexão")
        except Exception as e:
            self.text_area.insert(tk.END, f"Erro inesperado: {str(e)}\n", 'erro')
            self.status_var.set("Erro inesperado")
    
    def mostrar_detalhes_estruturados(self, dados):
        """Mostra os detalhes em formato estruturado"""
        try:
            # Dados atuais
            atual = dados.get('current_condition', [{}])[0]
            local = dados.get('nearest_area', [{}])[0]
            
            self.text_area.insert(tk.END, "📍 LOCALIZAÇÃO\n", 'subtitulo')
            self.text_area.insert(tk.END, f"Cidade: {local.get('areaName', [{}])[0].get('value', 'N/A')}\n")
            self.text_area.insert(tk.END, f"Região: {local.get('region', [{}])[0].get('value', 'N/A')}\n")
            self.text_area.insert(tk.END, f"País: {local.get('country', [{}])[0].get('value', 'N/A')}\n\n")
            
            self.text_area.insert(tk.END, "🌡️ CONDIÇÕES ATUAIS\n", 'subtitulo')
            self.text_area.insert(tk.END, f"Temperatura: {atual.get('temp_C', 'N/A')}°C\n")
            self.text_area.insert(tk.END, f"Sensação: {atual.get('FeelsLikeC', 'N/A')}°C\n")
            self.text_area.insert(tk.END, f"Condição: {atual.get('weatherDesc', [{}])[0].get('value', 'N/A')}\n")
            self.text_area.insert(tk.END, f"Umidade: {atual.get('humidity', 'N/A')}%\n")
            self.text_area.insert(tk.END, f"Velocidade do vento: {atual.get('windspeedKmph', 'N/A')} km/h\n")
            self.text_area.insert(tk.END, f"Direção do vento: {atual.get('winddir16Point', 'N/A')}\n")
            self.text_area.insert(tk.END, f"Pressão: {atual.get('pressure', 'N/A')} mb\n")
            self.text_area.insert(tk.END, f"Visibilidade: {atual.get('visibility', 'N/A')} km\n")
            self.text_area.insert(tk.END, f"UV Index: {atual.get('uvIndex', 'N/A')}\n")
            self.text_area.insert(tk.END, f"Nuvens: {atual.get('cloudcover', 'N/A')}%\n")
            
            # Previsão para os próximos dias
            previsao = dados.get('weather', [])
            if previsao:
                self.text_area.insert(tk.END, "\n📅 PREVISÃO PARA OS PRÓXIMOS DIAS\n", 'subtitulo')
                self.text_area.insert(tk.END, "-" * 50 + "\n")
                
                for dia in previsao[:3]:  # Mostrar apenas 3 dias
                    data = dia.get('date', 'N/A')
                    max_temp = dia.get('maxtempC', 'N/A')
                    min_temp = dia.get('mintempC', 'N/A')
                    condicao = dia.get('hourly', [{}])[0].get('weatherDesc', [{}])[0].get('value', 'N/A')
                    
                    self.text_area.insert(tk.END, f"📆 {data}: {condicao}\n")
                    self.text_area.insert(tk.END, f"   Máx: {max_temp}°C | Mín: {min_temp}°C\n\n")
            
            self.text_area.insert(tk.END, "=" * 60 + "\n")
            self.text_area.insert(tk.END, "Dados fornecidos por wttr.in\n", 'info')
            
        except Exception as e:
            self.text_area.insert(tk.END, f"Erro ao processar dados estruturados: {str(e)}\n", 'erro')
    
    def limpar_texto(self):
        """Limpa a área de texto"""
        self.text_area.delete(1.0, tk.END)
        self.status_var.set("Texto limpo")

def main():
    root = tk.Tk()
    app = PrevisaoTempoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()