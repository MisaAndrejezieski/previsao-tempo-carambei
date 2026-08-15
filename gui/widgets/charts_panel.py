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
