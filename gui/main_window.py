import tkinter as tk
from tkinter import ttk  # <-- ADICIONAR ESTA LINHA
import threading
from typing import Optional
from core.clima_service import ClimaService
from core.models import PrevisaoCompleta
from core.exceptions import ClimaException
from gui.styles import NeonTheme
from gui.widgets.search_panel import SearchPanel
from gui.widgets.weather_display import WeatherDisplay
from gui.widgets.charts_panel import ChartsPanel
from utils.logger import log