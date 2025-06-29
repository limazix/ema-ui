import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI


from langgraph.graph import StateGraph

### Define the Agent State ###
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]


### Define the agents ###

# Prompt template for the compliance report agent
compliance_report_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Você é um especialista em engenharia elétrica e regulamentações da ANEEL, encarregado de gerar um relatório técnico de conformidade detalhado e bem estruturado.
O relatório DEVE ser gerado no idioma especificado por '{languageCode}' (o padrão é Português do Brasil - pt-BR - se não especificado ou se o idioma não for bem suportado para esta tarefa técnica).
As citações diretas de nomes de resoluções, artigos da ANEEL ou textos de normas devem permanecer em Português, mesmo que o restante do relatório esteja em outro idioma.

Contexto da Análise:
- Arquivo de Dados Analisado: {fileName}
- Sumário dos Dados de Qualidade de Energia: {powerQualityDataSummary}
- Resoluções ANEEL Identificadas como Pertinentes (em Português): {identifiedRegulations}
- Idioma do Relatório: {languageCode}

Sua Tarefa:
Gerar um relatório de conformidade completo no idioma '{languageCode}', seguindo RIGOROSAMENTE a estrutura de saída JSON definida abaixo. O relatório deve ser técnico, claro, objetivo e pronto para ser a base de um documento PDF profissional.

Diretrizes Detalhadas para Cada Parte do Relatório (a serem geradas no idioma '{languageCode}'):

1.  reportMetadata:
    *   `title`: Crie um título formal, como "Relatório de Análise de Conformidade da Qualidade de Energia Elétrica".
    *   `subtitle`: Opcional. Pode incluir o nome do arquivo: "Análise referente ao arquivo '{fileName}'".
    *   `author`: Use "Energy Compliance Analyzer".
    *   `generatedDate`: Use a data atual no formato YYYY-MM-DD.

2.  tableOfContents:
    *   Liste os títulos das seções principais que você criará (Ex: "Introdução", títulos de `analysisSections`, "Considerações Finais", "Referências Bibliográficas").

3.  introduction:
    *   `objective`: Descreva o propósito do relatório (ex: analisar a conformidade dos dados de '{fileName}' com as resoluções ANEEL).
    *   `overallResultsSummary`: Forneça um breve panorama dos achados (ex: se a maioria dos parâmetros está conforme, ou se há violações significativas).
    *   `usedNormsOverview`: Mencione de forma geral as principais resoluções ANEEL (da lista {identifiedRegulations}, mantendo os nomes das resoluções em Português) que fundamentaram a análise.

4.  analysisSections (Array): Esta é a parte principal. Crie múltiplas seções.
    *   Ordenação: Organize as seções por temas comuns (ex: "Análise de Tensão", "Análise de Frequência", "Desequilíbrio de Tensão", "Harmônicos") e, dentro dos temas, se possível, de forma cronológica caso os dados no sumário permitam identificar eventos com data/hora.
    *   Para cada `ReportSectionSchema` no array:
        *   `title`: Um título claro e descritivo para a seção (ex: "Análise dos Níveis de Tensão em Regime Permanente").
        *   `content`: Detalhe a análise dos parâmetros relevantes para esta seção, baseado no `powerQualityDataSummary`. Seja técnico, mas claro. Compare os valores observados com os limites regulatórios.
        *   `insights`: Liste os principais insights, observações ou problemas detectados nesta seção específica. Cada insight deve ser uma frase concisa.
        *   `relevantNormsCited`: Para cada insight ou problema, **explicite a norma ANEEL e o artigo/item específico em Português** que o respalda (ex: "Resolução XXX/YYYY, Art. Z, Inciso W", ou "PRODIST Módulo 8, item 3.2.1"). Seja preciso.
        *   `chartOrImageSuggestion`: (OPCIONAL, MAS RECOMENDADO) Gere uma sugestão de diagrama visual em **sintaxe Mermaid** que poderia ilustrar os achados da seção. Ex: para um gráfico de pizza, `pie title Título do Gráfico "Seção A": 30 "Seção B": 70`; para um gráfico de barras, `xychart-beta title "Variação da Tensão" x-axis "Tempo" y-axis "Tensão (V)" bar [10, 12, 15, 11]`. **Consulte a documentação oficial do Mermaid.js em https://mermaid.js.org/intro/ para referência da sintaxe.** A sintaxe Mermaid DEVE ser fornecida diretamente neste campo.
        *   `chartUrl`: (OPCIONAL) Este campo será preenchido posteriormente com a URL de um gráfico gerado. Não preencha este campo.

5.  finalConsiderations:
    *   Resuma as principais conclusões da análise.
    *   Destaque os pontos mais críticos de não conformidade, se houver.
    *   Pode incluir recomendações gerais (se o sumário de dados permitir inferi-las).

6.  bibliography (Array):
    *   Para cada norma ANEEL que foi CITADA em `relevantNormsCited` em qualquer `analysisSections`:
        *   Crie um item `BibliographyItemSchema`.
        *   `text`: Forneça a referência completa da norma **em Português** (ex: "Agência Nacional de Energia Elétrica (ANEEL). Resolução Normativa nº 956, de 7 de dezembro de 2021. Estabelece os Procedimentos de Distribuição de Energia Elétrica no Sistema Elétrico Nacional – PRODIST."). Se for um módulo específico, cite-o (ex: "ANEEL. PRODIST Módulo 8 - Qualidade da Energia Elétrica. Revisão 2023.").
        *   `link`: Se você souber de um link oficial para a norma, inclua-o. Caso contrário, pode omitir.

Importante:
*   O conteúdo principal do relatório deve ser gerado no idioma '{languageCode}'.
*   Nomes de resoluções, artigos e textos normativos da ANEEL DEVEM ser mantidos em Português.
*   Seja o mais detalhado e preciso possível, baseando-se estritamente nas informações do `powerQualityDataSummary` e nas `identifiedRegulations`.
*   Se o sumário for limitado, reconheça isso em suas análises (ex: "Com base nos dados sumarizados, não foi possível avaliar X em detalhe...").
*   A qualidade da estruturação, a precisão das referências às normas e a validade da sintaxe Mermaid são cruciais.
*   Garanta que a saída seja um JSON válido que corresponda ao schema `AnalyzeComplianceReportOutputSchema`.

Retorne APENAS o objeto JSON do relatório. Não inclua nenhum texto explicativo antes ou depois do JSON.
""",
        ),
        ("human", "{input}"),
    ]
)

# Compliance Report Agent
def compliance_report_agent(state):
    """
    Generate a technical compliance report based on ANEEL regulations.
    """
    print("---GENERATING COMPLIANCE REPORT---")
    # Extract information from the state (assuming it's passed in the user message content)
    # In a real application, this would be structured data passed in the state
    # For this example, we'll parse from the last message
    last_message_content = state['messages'][-1].content if state['messages'] else ""
    # Assuming input format is a simple string for now, will need to be more structured
    # to pass all required parameters (fileName, powerQualityDataSummary, etc.)
    # For demonstration, let's assume the input string contains comma-separated values
    # like "fileName,powerQualityDataSummary,identifiedRegulations,languageCode"
    try:
        fileName, powerQualityDataSummary, identifiedRegulations, languageCode = last_message_content.split(",", 3)
    except ValueError:
        print("---Error parsing input for compliance report agent---")
        # Handle the error appropriately, maybe return an error message
        return {"messages": [("assistant", "Error: Invalid input format for compliance report generation.")]}

    # Create the chain
    chain = (
        RunnablePassthrough.assign(
            input=lambda x: f"Generate the ANEEL compliance report using the following data:\nFile Name: {x['fileName']}\nSummary: {x['powerQualityDataSummary']}\nRegulations: {x['identifiedRegulations']}\nLanguage: {x['languageCode']}"
        )
        | compliance_report_prompt # Using Gemini 1.5 Flash as it's cost-effective and good for structured outputs.
        | ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)  # Use a suitable model
        | JsonOutputParser()
    )

    # Invoke the chain with the extracted information
    compliance_report_content = chain.invoke({
        "fileName": fileName.strip(),
        "powerQualityDataSummary": powerQualityDataSummary.strip(),
        "identifiedRegulations": identifiedRegulations.strip(),
        "languageCode": languageCode.strip()
    })

    return {"messages": [("assistant", compliance_report_content)]}


### Define the graph ###
workflow = StateGraph(AgentState)

# Add the compliance report agent as a node
workflow.add_node("compliance_report", compliance_report_agent)

# Add the initial entry point
workflow.set_entry_point("compliance_report")

# Add a conditional edge to decide where to go after the report
# For this example, we'll just end the graph after the report is generated
workflow.set_finish_point("compliance_report")

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    # Example usage:
    # Example input string: "fileName,powerQualityDataSummary,identifiedRegulations,languageCode"
    example_input = "my_power_data.csv,Voltage is mostly within limits, but some dips observed. Frequency is stable. Harmonics are low.,Resolução Normativa nº 956/2021,PRODIST Módulo 8,pt-BR"

    inputs = {"messages": [("user", example_input)]}

    result = app.invoke(inputs)
    print(result)