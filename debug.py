"""Debug para verificar os dados"""

from core.clima_service import ClimaService
from core.models import PrevisaoCompleta
import json

def debug_previsao():
    service = ClimaService()
    
    print("🔍 Buscando previsão para Carambeí...")
    previsao = service.buscar_previsao("Carambeí")
    
    if previsao:
        print("\n✅ Previsão encontrada!")
        print(f"📍 Cidade: {previsao.atual.coordenadas.cidade}")
        print(f"🌡️ Temperatura atual: {previsao.atual.temperatura}°C")
        print(f"📅 Dias de previsão: {len(previsao.previsao_7dias)}")
        
        print("\n📊 PREVISÃO 7 DIAS:")
        for i, dia in enumerate(previsao.previsao_7dias, 1):
            print(f"  {i}. {dia.data.strftime('%d/%m')} - {dia.condicao.descricao}")
            print(f"     Máx: {dia.temp_max}°C | Mín: {dia.temp_min}°C")
            print(f"     Precipitação: {dia.precipitacao}mm")
    else:
        print("❌ Nenhuma previsão encontrada!")

if __name__ == "__main__":
    debug_previsao()