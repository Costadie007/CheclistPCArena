# Troque a senha do painel antes de publicar.
SENHA_PAINEL = 'arena2026'

# Arquivo onde o progresso fica salvo no servidor.
ARQUIVO_ESTADO = 'estado_arena.json'

NOME = 'PC Arena'
AVISO_TOPO = None
AVISOS_ANTES = ['Durante o culto: foco total, evite distrações e conversas desnecessárias.']
AVISO_DEPOIS = None

SECOES = {
    "Antes do culto": ['Checar se os disjuntores estão ligados', 'Ligar os projetores primeiro', 'Ligar o PC', 'Conferir se o PC está limpo de arquivos antigos', 'Limpar temp (Win+R > temp > apagar tudo)', 'Limpar %temp% (Win+R > %temp% > apagar tudo)', 'Limpar prefetch (Win+R > prefetch > apagar tudo)', 'Esvaziar a lixeira (Win+R > shell:RecycleBinFolder > apagar tudo)', 'Conferir se os banners do dia/evento estão atualizados', 'Conferir se o vídeo (se houver) está na velocidade correta'],
    "Depois do culto": ['Apagar todos os arquivos baixados no dia', 'Dar uma geral no PC', 'Deixar a mesa organizada para a próxima equipe', 'Desligar o PC', 'Desligar todos os projetores (confirmar que desligaram mesmo)'],
}

import json
import os

import streamlit as st
from streamlit_autorefresh import st_autorefresh


def carregar_estado():
    """Le o progresso salvo no arquivo. Se nao existir, comeca vazio."""
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    return {}


def salvar_estado(estado):
    """Grava o progresso atual no arquivo."""
    with open(ARQUIVO_ESTADO, "w", encoding="utf-8") as arquivo:
        json.dump(estado, arquivo, ensure_ascii=False, indent=2)


st.set_page_config(page_title=f"Checklist {NOME}", page_icon="✅")

if "estado" not in st.session_state:
    st.session_state.estado = carregar_estado()

modo = st.radio(
    "Modo",
    ["Marcar itens", "Painel de acompanhamento (tempo real)"],
    horizontal=True,
)

total_itens = sum(len(lista) for lista in SECOES.values())

if modo == "Painel de acompanhamento (tempo real)":
    if "painel_autenticado" not in st.session_state:
        st.session_state.painel_autenticado = False

    if not st.session_state.painel_autenticado:
        st.title(f"Painel {NOME}")
        senha_digitada = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if senha_digitada == SENHA_PAINEL:
                st.session_state.painel_autenticado = True
                st.rerun()
            else:
                st.error("Senha incorreta.")
        st.stop()

    # Atualiza sozinho a cada 3 segundos pra refletir o que outras pessoas marcam.
    st_autorefresh(interval=3000, key="atualizacao_painel")

    st.title(f"Painel {NOME}")
    st.caption("Atualiza sozinho a cada 3 segundos. Somente leitura.")

    # Sempre le do arquivo, porque quem marca esta em outra sessao.
    estado_geral = carregar_estado()
    feitos = sum(
        1 for chave, valor in estado_geral.items()
        if chave.startswith("item-") and valor
    )
    voluntario = estado_geral.get("voluntario", "").strip()
    st.write(f"Voluntário na operação: {voluntario or 'não informado'}")

    st.progress(feitos / total_itens if total_itens else 0)
    st.write(f"{feitos} de {total_itens} concluídos")

    for secao, lista in SECOES.items():
        with st.expander(secao, expanded=True):
            for indice, texto in enumerate(lista):
                marcado = estado_geral.get(f"item-{secao}-{indice}", False)
                simbolo = "✅" if marcado else "⬜"
                st.write(f"{simbolo} {texto}")

    st.stop()

st.title(f"Checklist {NOME}")
st.caption("Marque cada item conforme for concluindo. O progresso fica salvo.")

if AVISO_TOPO:
    st.warning(AVISO_TOPO)

nome_voluntario = st.text_input(
    "Nome do voluntário na operação",
    value=st.session_state.estado.get("voluntario", ""),
    key="voluntario_input",
)
if nome_voluntario != st.session_state.estado.get("voluntario", ""):
    st.session_state.estado["voluntario"] = nome_voluntario
    salvar_estado(st.session_state.estado)

total_feitos = sum(
    1 for chave, valor in st.session_state.estado.items()
    if chave.startswith("item-") and valor
)
st.progress(total_feitos / total_itens if total_itens else 0)
st.write(f"{total_feitos} de {total_itens} concluídos")

st.divider()

for secao, lista_itens in SECOES.items():
    st.subheader(secao)
    for indice, texto in enumerate(lista_itens):
        chave = f"item-{secao}-{indice}"
        marcado = st.session_state.estado.get(chave, False)
        novo_valor = st.checkbox(texto, value=marcado, key=chave)
        if novo_valor != marcado:
            st.session_state.estado[chave] = novo_valor
            salvar_estado(st.session_state.estado)

    if secao == "Antes do culto":
        for aviso in AVISOS_ANTES:
            st.info(aviso)
        st.divider()

    if secao == "Depois do culto" and AVISO_DEPOIS:
        st.warning(AVISO_DEPOIS)

st.divider()

if st.button("Reiniciar checklist", type="secondary"):
    st.session_state.estado = {}
    # Os checkboxes guardam o proprio valor em st.session_state com a mesma
    # chave. Sem apagar isso, continuam marcados na tela apos o reset.
    for chave in list(st.session_state.keys()):
        if chave.startswith("item-") or chave == "voluntario_input":
            del st.session_state[chave]
    salvar_estado(st.session_state.estado)
    st.rerun()

st.caption(
    "Tudo que vem da gestão são ordens pastorais. Primeiro execute o que foi "
    "pedido; sugestões só depois, direto com a gestão."
)
