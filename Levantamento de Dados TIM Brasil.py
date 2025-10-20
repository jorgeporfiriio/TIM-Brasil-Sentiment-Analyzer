import requests
import time
import json
from datetime import datetime, timedelta
import pandas as pd

BEARER_TOKEN = ""

headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}


def classificar_sentimento(texto):
    if not texto or len(texto.strip()) == 0:
        return "Neutra"
    
    texto = texto.lower()
    
    
    palavras_positivas = [
        'bom', 'boa', 'ótimo', 'excelente', 'gostei', 'recomendo', 'rápido', 
        'funciona', 'atendimento bom', 'resolveram', 'solucionou', 'eficiente',
        'qualidade', 'estável', 'conseguiu', 'parabéns', 'obrigado', 'thanks',
        'resolveu', 'sucesso', 'feliz', 'satisfeito', 'content', 'top', 'show'
    ]
    
    palavras_negativas = [
        'ruim', 'péssimo', 'horrível', 'lento', 'não funciona', 'problema', 
        'reclamação', 'lentidão', 'queda', 'indisponível', 'horrivel', 'pessimo',
        'atendimento ruim', 'não resolve', 'insatisfeito', 'decepcionado',
        'reclamo', 'reclamar', 'procop', 'procon', 'processo', 'processar',
        'cancelar', 'cancelamento', 'odeio', 'péssima', 'nunca mais', 'detesto',
        'incapaz', 'incompetente', 'vergonha', 'absurdo', 'inaceitável'
    ]
    
    positivas = sum(1 for palavra in palavras_positivas if palavra in texto)
    negativas = sum(1 for palavra in palavras_negativas if palavra in texto)
    
    if positivas > negativas:
        return "Positiva"
    elif negativas > positivas:
        return "Negativa"
    else:
        return "Neutra"


def buscar_tweets_com_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            url = f"https://api.x.com/2/tweets/search/recent?query={query}&max_results=100&tweet.fields=created_at,text"
            
            r = requests.get(url, headers=headers)
            
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 429:
                print(f"⏰ Rate limit atingido. Tentativa {attempt + 1}/{max_retries}")
                if 'x-rate-limit-reset' in r.headers:
                    reset_time = int(r.headers['x-rate-limit-reset'])
                    wait_time = reset_time - time.time() + 10
                    print(f"🕒 Aguardando {wait_time:.0f} segundos...")
                    time.sleep(max(wait_time, 60))
                else:
                    print("⏳ Aguardando 15 minutos...")
                    time.sleep(900)  # 15 minutos
            else:
                print(f"❌ Erro {r.status_code}: {r.text}")
                return None
                
        except Exception as e:
            print(f"⚠️ Erro na requisição: {e}")
            time.sleep(30)
    
    return None

def gerar_dados_simulados():
    print("📊 Gerando dados simulados para demonstração...")
    
    resultados = {}
    base_date = datetime(2025, 10, 1)
    
    for i in range(5):
        current_date = base_date + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        
        resultados[date_str] = {
            "Positiva": max(5, 15 + i * 2),  # Aumenta levemente
            "Negativa": max(3, 8 + i),       # Aumenta moderadamente
            "Neutra": max(8, 12 + i)         # Mantém estável
        }
    
    return resultados


def analisar_mentions_tim():
    print("🔍 Iniciando análise de menções à TIM Brasil...")
    
    query = "@timbrasil -is:retweet"
    dados = buscar_tweets_com_retry(query)
    
    if dados is None:
        print("🚨 Não foi possível acessar a API. Usando dados simulados para demonstração.")
        resultados = gerar_dados_simulados()
    elif 'data' in dados and dados['data']:
        resultados = {}
        for tweet in dados['data']:
            data_tweet = tweet['created_at'][:10]
            texto = tweet['text']
            sentimento = classificar_sentimento(texto)
            
            if data_tweet not in resultados:
                resultados[data_tweet] = {"Positiva": 0, "Negativa": 0, "Neutra": 0}
            
            resultados[data_tweet][sentimento] += 1
    else:
        print("📭 Nenhum tweet encontrado. Usando dados simulados.")
        resultados = gerar_dados_simulados()
    
    return resultados


resultados = analisar_mentions_tim()


print("\n" + "="*60)
print("📊 RELATÓRIO - MENÇÕES TIM BRASIL (ANÁLISE DE SENTIMENTO)")
print("="*60)

if resultados:
 
    datas_ordenadas = sorted(resultados.keys())
    
    for data in datas_ordenadas:
        stats = resultados[data]
        total = sum(stats.values())
        
        print(f"\n📅 {data}:")
        print(f"   ✅ Positivas: {stats['Positiva']:2d} ({stats['Positiva']/total*100:5.1f}%)")
        print(f"   ❌ Negativas: {stats['Negativa']:2d} ({stats['Negativa']/total*100:5.1f}%)")
        print(f"   ⚪ Neutras:   {stats['Neutra']:2d} ({stats['Neutra']/total*100:5.1f}%)")
        print(f"   📊 Total:     {total:2d} menções")
    
    
    print("\n" + "="*60)
    print("📈 RESUMO CONSOLIDADO")
    print("="*60)
    
    total_positivas = sum(dia['Positiva'] for dia in resultados.values())
    total_negativas = sum(dia['Negativa'] for dia in resultados.values())
    total_neutras = sum(dia['Neutra'] for dia in resultados.values())
    total_geral = total_positivas + total_negativas + total_neutras
    
    if total_geral > 0:
        print(f"   ✅ Positivas: {total_positivas:3d} ({total_positivas/total_geral*100:5.1f}%)")
        print(f"   ❌ Negativas: {total_negativas:3d} ({total_negativas/total_geral*100:5.1f}%)")
        print(f"   ⚪ Neutras:   {total_neutras:3d} ({total_neutras/total_geral*100:5.1f}%)")
        print(f"   📊 Total Geral: {total_geral:3d} menções")
        
     
        nss = (total_positivas - total_negativas) / total_geral * 100
        print(f"   🎯 Net Sentiment Score: {nss:+.1f}%")
        
     
        if nss > 20:
            print("   📈 Tendência: Muito Positiva")
        elif nss > 5:
            print("   📈 Tendência: Positiva")
        elif nss > -5:
            print("   ➡️ Tendência: Neutra")
        elif nss > -20:
            print("   📉 Tendência: Negativa")
        else:
            print("   📉 Tendência: Muito Negativa")
    
   
    df = pd.DataFrame.from_dict(resultados, orient='index')
    df.to_csv('analise_tim_mentions.csv', encoding='utf-8-sig')
    print(f"\n💾 Dados exportados para 'analise_tim_mentions.csv'")
    
else:
    print("❌ Nenhum dado disponível para análise.")