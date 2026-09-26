import json
import os

import streamlit as st

# Arquivo onde o progresso fica salvo no servidor.
# Assim, se alguém fechar a aba e abrir de novo, o progresso continua lá.
ARQUIVO_ESTADO = "estado_checklist.json"

ITENS = {
    "Antes do culto": [
        "Checar se os disjuntores estão ligados",
        "Ligar os projetores primeiro",
        "Ligar o PC",
        "Conferir se o PC está limpo de arquivos antigos",
        "Limpar temp (Win+R > temp > apagar tudo)",
        "Limpar %temp% (Win+R > %temp% > apagar tudo)",
        "Limpar prefetch (Win+R > prefetch > apagar tudo)",
        "Esvaziar a lixeira (Win+R > shell:RecycleBinFolder > apagar tudo)",
        "Conferir se os banners do dia/evento estão atualizados",
        "Conferir se o vídeo (se houver) está na velocidade correta",
    ],
    "Depois do culto": [
        "Apagar todos os arquivos baixados no dia",
        "Dar uma geral no PC",
        "Deixar a mesa organizada para a próxima equipe",
        "Desligar o PC",
        "Desligar todos os projetores (confirmar que desligaram mesmo)",
    ],
}


def carregar_estado():
    """Lê o progresso salvo no arquivo. Se não existir, começa vazio."""
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return {}


def salvar_estado(estado):
    """Grava o progresso atual no arquivo."""
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as arquivo:
        json.dump(estado, arquivo, ensure_ascii=False, indent=2)


# session_state guarda o estado durante a sessão do navegador.
# Na primeira vez que o app roda, carregamos do arquivo.
if "estado" not in st.session_state:
    st.session_state.estado = carregar_estado()

st.set_page_config(page_title="Checklist PC Arena", page_icon="✅")

st.title("Checklist PC Arena")
st.caption("Marque cada item conforme for concluindo. O progresso fica salvo.")

# Calcula o progresso geral somando todos os itens de todas as seções.
total_itens = sum(len(lista) for lista in ITENS.values())
total_feitos = sum(1 for valor in st.session_state.estado.values() if valor)

st.progress(total_feitos / total_itens if total_itens else 0)
st.write(f"{total_feitos} de {total_itens} concluídos")

st.divider()

for secao, lista_itens in ITENS.items():
    st.subheader(secao)
    for indice, texto in enumerate(lista_itens):
        chave = f"{secao}-{indice}"
        marcado = st.session_state.estado.get(chave, False)
        novo_valor = st.checkbox(texto, value=marcado, key=chave)
        if novo_valor != marcado:
            st.session_state.estado[chave] = novo_valor
            salvar_estado(st.session_state.estado)

    if secao == "Antes do culto":
        st.info(
            "Durante o culto: foco total, evite distrações e conversas "
            "desnecessárias."
        )
        st.divider()

st.divider()

if st.button("Reiniciar checklist", type="secondary"):
    st.session_state.estado = {}
    salvar_estado(st.session_state.estado)
    st.rerun()

st.caption(
    "Tudo que vem da gestão são ordens pastorais. Primeiro execute o que foi "
    "pedido; sugestões só depois, direto com a gestão."
)
