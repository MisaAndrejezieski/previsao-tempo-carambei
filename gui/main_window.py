import threading
import tkinter as tk
from tkinter import ttk
from typing import Optional

from core.clima_service import ClimaService
from core.exceptions import ClimaException
from core.models import PrevisaoCompleta
from gui.styles import NeonTheme
from gui.widgets.charts_panel import ChartsPanel
from gui.widgets.search_panel import SearchPanel
from gui.widgets.weather_display import WeatherDisplay
from utils.logger import log
