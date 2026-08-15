"""Widget para exibir informações do clima"""

import tkinter as tk
from datetime import datetime
from tkinter import scrolledtext
from typing import Optional

from core.models import PrevisaoCompleta
from gui.styles import NeonTheme
from utils.logger import log


class WeatherDisplay(tk.Frame):
    """Exibe informações do clima"""
    
    def __init__(self, parent, theme: NeonTheme, clima_service):
        super().__init__(parent, bg=theme.bg)
        self.theme = theme
        self.clima_service = clima_service
        self.previsao: Optional[PrevisaoCompleta] = None
        
        self._criar_widgets()
        self._configurar_tags()
    
    def _criar_widgets(self):
        """Cria os widgets de exibição"""
        self.text_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=self.theme.bg,
            fg=self.theme.texto_claro,
            insertbackground=self.theme.neon_verde,
            relief=tk.FLAT,
            padx=15,
            pady=15
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _configurar_tags(self):
        """Configura tags de formatação"""
        tags = {
            'titulo': ('Segoe UI', 16, 'bold', self.theme.neon_azul),
            'subtitulo': ('Segoe UI', 13, 'bold', self.theme.neon_roxo),
            'destaque': ('Segoe UI', 12, 'bold', self.theme.neon_verde),
            'info': ('Segoe UI', 11, self.theme.neon_rosa),
            'separador': ('Segoe UI', 10, self.theme.neon_amarelo),
            'erro': ('Segoe UI', 11, 'bold', self.theme.neon_vermelho),
            'neon_laranja': ('Segoe UI', 11, self.theme.neon_laranja),
            'neon_dourado': ('Segoe UI', 11, 'bold', self.theme.neon_dourado)
        }
        
        for nome, (fonte, tamanho, *resto) in tags.items():
            if len(resto) == 1:
                self.text_area.tag_configure(nome, font=(fonte, tamanho), foreground=resto[0])
            elif len(resto) == 2:
                self.text_area.tag_configure(nome, font=(fonte, tamanho, resto[0]), foreground=resto[1])
    
    def atualizar(self, previsao: PrevisaoCompleta):
        """Atualiza com novos dados - MOSTRA A PREVISÃO COMPLETA!"""
        self.previsao = previsao
        self.text_area.delete(1.0, tk.END)
        
        atual = previsao.atual
        coords = atual.coordenadas
        
        # ============ CABEÇALHO ============
        self.text_area.insert(tk.END, "✦" * 45 + "\n", 'separador')
        self.text_area.insert(tk.END, f"  🌸 {coords.cidade.upper()} - {coords.pais} 🌸\n", 'titulo')
        if coords.regiao:
            self.text_area.insert(tk.END, f"  📍 {coords.regiao}\n", 'info')
        self.text_area.insert(tk.END, "✦" * 45 + "\n\n", 'separador')
        
        # ============ CLIMA ATUAL ============
        condicao = atual.condicao
        self.text_area.insert(tk.END, "🌡️ CLIMA ATUAL\n", 'subtitulo')
        self.text_area.insert(tk.END, f"  {condicao.icone} {condicao.descricao}\n\n", 'destaque')
        self.text_area.insert(tk.END, f"  🌡️  Temperatura: {atual.temperatura}°C\n", 'neon_laranja')
        self.text_area.insert(tk.END, f"  🌡️  Sensação: {atual.sensacao_termica}°C\n", 'info')
        self.text_area.insert(tk.END, f"  💧  Umidade: {atual.umidade}%\n", 'info')
        self.text_area.insert(tk.END, f"  💨  Vento: {atual.vento_kmh} km/h\n", 'info')
        self.text_area.insert(tk.END, f"  🌧️  Precipitação: {atual.precipitacao} mm\n", 'info')
        self.text_area.insert(tk.END, f"  ☁️  Nuvens: {atual.nuvens}%\n\n", 'info')
        
        # ============ PREVISÃO 7 DIAS ============
        if previsao.previsao_7dias:
            self.text_area.insert(tk.END, "📅 PREVISÃO 7 DIAS\n", 'subtitulo')
            self.text_area.insert(tk.END, "─" * 45 + "\n", 'separador')
            
            dias_semana = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO', 'DOMINGO']
            
            for i, dia in enumerate(previsao.previsao_7dias[:7]):
                nome_dia = dias_semana[dia.data.weekday()]
                data_formatada = dia.data.strftime('%d/%m')
                
                # Dia
                self.text_area.insert(tk.END, f"\n  📆 {nome_dia} - {data_formatada}\n", 'destaque')
                
                # Condição
                self.text_area.insert(tk.END, f"     {dia.condicao.icone} {dia.condicao.descricao}\n", 'info')
                
                # Temperaturas
                self.text_area.insert(tk.END, f"     🔥 Máx: {dia.temp_max}°C", 'neon_laranja')
                self.text_area.insert(tk.END, f"  ❄️ Mín: {dia.temp_min}°C\n", 'neon_laranja')
                
                # Precipitação
                if dia.precipitacao > 0:
                    self.text_area.insert(tk.END, f"     🌧️  Precipitação: {dia.precipitacao} mm\n", 'info')
                else:
                    self.text_area.insert(tk.END, f"     ☀️  Sem chuva prevista\n", 'info')
            
            self.text_area.insert(tk.END, "\n" + "✦" * 45 + "\n", 'separador')
        else:
            self.text_area.insert(tk.END, "\n⚠️ Nenhuma previsão disponível\n", 'erro')
        
        # ============ RODAPÉ ============
        self.text_area.insert(tk.END, f"\n🕐 Atualizado: {atual.atualizado_em.strftime('%d/%m/%Y %H:%M')}\n", 'info')
        self.text_area.insert(tk.END, "✦" * 45 + "\n", 'separador')
        self.text_area.insert(tk.END, "💫 Dados fornecidos por Open-Meteo\n", 'info')
        
        log.debug(f"Clima de {coords.cidade} atualizado com {len(previsao.previsao_7dias)} dias de previsão")
    
    def mostrar_detalhes(self):
        """Mostra detalhes completos com previsão"""
        if not self.previsao:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "⚠️ Nenhum dado disponível\n", 'erro')
            return
        
        # Simplesmente chama atualizar novamente
        self.atualizar(self.previsao)
    
    def mostrar_previsao(self):
        """Mostra apenas a previsão (atalho)"""
        if not self.previsao:
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "⚠️ Nenhum dado disponível\n", 'erro')
            return
        
        # Mostra a previsão completa novamente
        self.atualizar(self.previsao)
        self.text_area.insert(tk.END, "\n📌 Pressione Ctrl+D para detalhes\n", 'info')
    
    def mostrar_erro(self, mensagem: str):
        """Mostra mensagem de erro"""
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, f"❌ {mensagem}\n", 'erro')