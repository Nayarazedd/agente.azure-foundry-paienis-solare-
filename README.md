# Agente de IA - Limpeza e Manutenção de Painéis Solares

Sistema inteligente desenvolvido com Azure AI Foundry e Streamlit, projetado para auxiliar na gestão de limpeza, eficiência e manutenção preditiva de painéis solares fotovoltaicos, utilizando um banco de dados SQLite local para histórico e auditoria.

## System Prompt (Instruções Principais)
> "Você é um engenheiro especialista em manutenção e otimização de painéis solares fotovoltaicos. Responda de forma técnica e prática."

## Ferramentas (Functions) Mapeadas
1. **`consultar_prompt(item_id: int)`**: Realiza leitura no banco SQLite `painel_solar.db` na tabela `produtos` buscando os dados do prompt enviado, resposta gerada, data/hora e status.
2. **`verificar_prompt(item_id: int)`**: Realiza operação de atualização (UPDATE) no banco SQLite alterando o status do atendimento/manutenção para 'Verificado/Concluído'.

## Tecnologias Utilizadas
- Python 3.13
- Streamlit (Interface Gráfica)
- Azure OpenAI / Azure AI Foundry (`AzureOpenAI`)
- SQLite3 (Persistência local)