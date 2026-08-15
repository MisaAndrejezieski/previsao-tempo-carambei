"""Widget para gráficos e mapas"""

import os
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Optional

import folium
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.models import PrevisaoCompleta
from gui.styles import NeonTheme
from utils.logger import log


class ChartsPanel(tk.Frame):
    """Painel de gráficos e visualizações"""
    
    def __init__(self, parent, theme: NeonTheme, clima_service):
        super().__init__(parent, bg=theme.bg)
        self.theme = theme
        self.clima_service = clima_service
        self.previsao: Optional[PrevisaoCompleta] = None
        self.fig_atual = None
        
        self._criar_widgets()
    
    def _criar_widgets(self):
        """Cria os widgets do painel"""
        # Frame de controle
        control_frame = tk.Frame(self, bg=self.theme.bg)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botões
        botoes = [
            ("📊 Gráfico", self.mostrar_grafico, self.theme.neon_azul),
            ("🗺️ Mapa", self.mostrar_mapa, self.theme.neon_verde),
            ("💾 Salvar", self.salvar_grafico, self.theme.neon_roxo)
        ]
        
        for texto, comando, cor in botoes:
            btn = tk.Button(
                control_frame,
                text=texto,
                font=('Segoe UI', 10, 'bold'),
                fg=self.theme.bg,
                bg=cor,
                relief=tk.FLAT,
                padx=15,
                pady=8,
                cursor='hand2',
                command=comando
            )
            btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para conteúdo
        self.content_frame = tk.Frame(self, bg=self.theme.bg)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
    
    def atualizar(self, previsao: PrevisaoCompleta):
        """Atualiza com novos dados"""
        self.previsao = previsao
        log.debug("ChartsPanel atualizado")
    
    def mostrar_grafico(self):
        """Mostra gráfico de temperatura"""
        if not self.previsao:
            messagebox.showwarning("Aviso", "Nenhum dado disponível")
            return
        
        # Limpar frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Dados
        dias = self.previsao.previsao_7dias
        datas = [dia.data for dia in dias]
        temp_max = [dia.temp_max for dia in dias]
        temp_min = [dia.temp_min for dia in dias]
        precip = [dia.precipitacao for dia in dias]
        
        # Criar figura
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='#0a0a1a')
        
        # Gráfico de temperatura
        ax1.plot(datas, temp_max, color='#ff6b9d', marker='o', linewidth=2, label='Máxima')
        ax1.plot(datas, temp_min, color='#4ecdc4', marker='s', linewidth=2, label='Mínima')
        ax1.fill_between(datas, temp_min, temp_max, alpha=0.3, color='#a29bfe')
        ax1.set_title('Temperatura', color='#f0f0f0', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Temperatura (°C)', color='#f0f0f0')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#1a1a3e')
        ax1.tick_params(colors='#f0f0f0')
        
        # Gráfico de precipitação
        ax2.bar(datas, precip, color='#7bed9f', alpha=0.7)
        ax2.set_title('Precipitação', color='#f0f0f0', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Precipitação (mm)', color='#f0f0f0')
        ax2.set_xlabel('Data', color='#f0f0f0')
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#1a1a3e')
        ax2.tick_params(colors='#f0f0f0')
        
        # Formatar datas
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        
        # Mostrar
        canvas = FigureCanvasTkAgg(fig, self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig_atual = fig
        log.info("Gráfico gerado")
    
    def mostrar_mapa(self):
        """Mostra mapa interativo"""
        if not self.previsao:
            messagebox.showwarning("Aviso", "Nenhum dado disponível")
            return
        
        coords = self.previsao.atual.coordenadas
        
        try:
            mapa = folium.Map(
                location=[coords.latitude, coords.longitude],
                zoom_start=13,
                tiles='CartoDB dark_matter',
                control_scale=True
            )
            
            folium.Marker(
                [coords.latitude, coords.longitude],
                popup=f'<b>{coords.cidade}</b><br>{coords.pais}',
                tooltip=f'Clique para detalhes',
                icon=folium.Icon(color='pink', icon='cloud', prefix='fa')
            ).add_to(mapa)
            
            folium.Circle(
                [coords.latitude, coords.longitude],
                radius=1000,
                color='#ff6b9d',
                fill=True,
                fill_color='#ff6b9d',
                fill_opacity=0.2
            ).add_to(mapa)
            
            mapa_path = os.path.join(os.getcwd(), f'mapa_{coords.cidade}.html')
            mapa.save(mapa_path)
            webbrowser.open(f'file://{mapa_path}')
            
            log.info(f"Mapa gerado para {coords.cidade}")
            
        except Exception as e:
            log.error(f"Erro ao gerar mapa: {e}")
            messagebox.showerror("Erro", f"Erro ao gerar mapa: {str(e)}")
    
    def salvar_grafico(self):
        """Salva o gráfico como imagem"""
        if not self.fig_atual:
            messagebox.showwarning("Aviso", "Nenhum gráfico para salvar")
            return
        
        try:
            cidade = self.previsao.atual.coordenadas.cidade
            nome_arquivo = f"grafico_{cidade}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            self.fig_atual.savefig(
                nome_arquivo,
                dpi=300,
                bbox_inches='tight',
                facecolor='#0a0a1a',
                edgecolor='none'
            )
            
            messagebox.showinfo("Sucesso", f"Gráfico salvo como:\n{nome_arquivo}")
            log.info(f"Gráfico salvo: {nome_arquivo}")
            
        except Exception as e:
            log.error(f"Erro ao salvar gráfico: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {str(e)}")