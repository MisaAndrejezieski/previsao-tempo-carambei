"""Widget de busca de cidades"""

import os
import pickle
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from gui.styles import NeonTheme


class SearchPanel(tk.Frame):
    """Painel de busca de cidades"""
    
    def __init__(self, parent, theme: NeonTheme, on_search: Callable):
        super().__init__(parent, bg=theme.bg)
        self.theme = theme
        self.on_search = on_search
        self.historico = []
        
        self._criar_widgets()
        self._carregar_historico()
    
    def _criar_widgets(self):
        """Cria os widgets do painel"""
        # Frame de busca
        search_frame = tk.Frame(self, bg=self.theme.bg_frame, relief=tk.RAISED, bd=2)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            search_frame,
            text="🌆 Buscar Cidade",
            font=('Segoe UI', 12, 'bold'),
            fg=self.theme.neon_verde,
            bg=self.theme.bg_frame
        ).pack(pady=(10, 5))
        
        # Entry
        self.cidade_var = tk.StringVar()
        self.entry = tk.Entry(
            search_frame,
            textvariable=self.cidade_var,
            font=('Segoe UI', 11),
            bg=self.theme.bg,
            fg=self.theme.texto_claro,
            insertbackground=self.theme.neon_verde,
            relief=tk.FLAT
        )
        self.entry.pack(fill=tk.X, padx=10, pady=5)
        self.entry.bind('<Return>', lambda e: self.buscar())
        
        # Botão buscar
        self.btn_buscar = tk.Button(
            search_frame,
            text="🔍 BUSCAR CLIMA",
            font=('Segoe UI', 10, 'bold'),
            fg=self.theme.bg,
            bg=self.theme.neon_azul,
            activebackground=self.theme.neon_verde,
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.buscar
        )
        self.btn_buscar.pack(fill=tk.X, padx=10, pady=5)
        
        # Sugestões
        tk.Label(
            search_frame,
            text="📍 Sugestões Rápidas",
            font=('Segoe UI', 10),
            fg=self.theme.neon_amarelo,
            bg=self.theme.bg_frame
        ).pack(pady=(10, 5))
        
        sugestoes_frame = tk.Frame(search_frame, bg=self.theme.bg_frame)
        sugestoes_frame.pack(fill=tk.X, padx=10, pady=5)
        
        cidades_sugeridas = ["Carambeí", "Curitiba", "São Paulo", "Rio de Janeiro", "Brasília"]
        for cidade in cidades_sugeridas:
            btn = tk.Button(
                sugestoes_frame,
                text=cidade,
                font=('Segoe UI', 8),
                fg=self.theme.bg,
                bg=self.theme.neon_roxo,
                activebackground=self.theme.neon_azul,
                activeforeground=self.theme.bg,
                relief=tk.FLAT,
                padx=8,
                pady=3,
                cursor='hand2',
                command=lambda c=cidade: self.set_cidade(c)
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Histórico
        tk.Label(
            self,
            text="📜 Histórico",
            font=('Segoe UI', 10, 'bold'),
            fg=self.theme.neon_amarelo,
            bg=self.theme.bg
        ).pack(pady=(10, 5))
        
        self.historico_listbox = tk.Listbox(
            self,
            height=5,
            bg=self.theme.bg_frame,
            fg=self.theme.texto_claro,
            selectbackground=self.theme.neon_azul,
            relief=tk.FLAT,
            font=('Segoe UI', 9)
        )
        self.historico_listbox.pack(fill=tk.X, pady=5)
        self.historico_listbox.bind('<Double-Button-1>', self._carregar_do_historico)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=100
        )
        self.progress.pack(fill=tk.X, pady=5)
        self.progress.pack_forget()
    
    def buscar(self):
        """Dispara a busca"""
        cidade = self.cidade_var.get().strip()
        if cidade:
            self.on_search(cidade)
    
    def get_cidade(self) -> str:
        """Retorna o nome da cidade"""
        return self.cidade_var.get().strip()
    
    def set_cidade(self, cidade: str):
        """Define a cidade e busca"""
        self.cidade_var.set(cidade)
        self.buscar()
    
    def adicionar_historico(self, cidade: str):
        """Adiciona cidade ao histórico"""
        if cidade not in self.historico:
            self.historico.append(cidade)
            self._salvar_historico()
            self._atualizar_historico()
    
    def mostrar_carregando(self, ativo: bool):
        """Mostra/oculta barra de progresso"""
        if ativo:
            self.progress.pack(fill=tk.X, pady=5)
            self.progress.start()
            self.btn_buscar.config(state=tk.DISABLED)
        else:
            self.progress.stop()
            self.progress.pack_forget()
            self.btn_buscar.config(state=tk.NORMAL)
    
    def _carregar_do_historico(self, event):
        """Carrega cidade do histórico"""
        try:
            index = self.historico_listbox.curselection()[0]
            cidade = self.historico_listbox.get(index)
            self.cidade_var.set(cidade)
            self.buscar()
        except:
            pass
    
    def _atualizar_historico(self):
        """Atualiza listbox do histórico"""
        self.historico_listbox.delete(0, tk.END)
        for cidade in reversed(self.historico[-10:]):
            self.historico_listbox.insert(tk.END, cidade)
    
    def _carregar_historico(self):
        """Carrega histórico do disco"""
        try:
            if os.path.exists('historico.pkl'):
                with open('historico.pkl', 'rb') as f:
                    self.historico = pickle.load(f)
                self._atualizar_historico()
        except:
            pass
    
    def _salvar_historico(self):
        """Salva histórico no disco"""
        try:
            with open('historico.pkl', 'wb') as f:
                pickle.dump(self.historico[-20:], f)
        except:
            pass