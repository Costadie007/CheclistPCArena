import json
import os

import streamlit as st

# Arquivo onde o progresso fica salvo no servidor.
# Assim, se alguém fechar a aba e abrir de novo, o progresso continua lá.
ARQUIVO_ESTADO = "estado_checklist.json"

ROTEIROS = {
    "PC Arena": {
        "aviso_topo": None,
        "secoes": {
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
        },
    },
    "PC Holyrics": {
        "aviso_topo": "Aqui é exigido muita atenção à palavra e às letras no louvor.",
        "secoes": {
            "Antes do culto": [
                "Ligar o projetor",
                "Ligar o PC",
                "Conferir se o PC está limpo de arquivos antigos",
                "Limpar temp (Win+R > temp > apagar tudo)",
                "Limpar %temp% (Win+R > %temp% > apagar tudo)",
                "Limpar prefetch (Win+R > prefetch > apagar tudo)",
                "Esvaziar a lixeira (Win+R > shell:RecycleBinFolder > apagar tudo)",
                "Conferir se todas as letras que serão usadas estão prontas",
                "Prestar atenção às instruções do atmosfera e conferir as músicas do dia com o ministro",
            ],
            "Depois do culto": [
                "Apagar todos os arquivos baixados no dia",
                "Dar uma geral no PC",
                "Deixar a mesa organizada para a próxima equipe",
                "Desligar o PC",
                "Desligar todos os projetores (confirmar que desligaram mesmo)",
            ],
        },
    },
    "Iluminação": {
        "aviso_topo": None,
        "secoes": {
            "Antes do culto": [
                "Checar se os disjuntores estão ligados",
                "Ligar todos os equipamentos (Parleds, Movies e fumaça)",
                "Posicionar tudo da melhor forma possível",
                "Testar tudo antes de começar o evento",
            ],
            "Depois do culto": [
                "Desligar todos os equipamentos da tomada",
                "Desligar a mesa de luz",
                "Deixar a mesa organizada para a próxima equipe",
                "Combinar com o operador do PC Arena quem desliga os disjuntores",
            ],
        },
    },
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

st.set_page_config(page_title="Checklist Telão", page_icon="✅")

nome_roteiro = st.selectbox("Roteiro", list(ROTEIROS.keys()))
roteiro = ROTEIROS[nome_roteiro]

st.title(f"Checklist {nome_roteiro}")
st.caption("Marque cada item conforme for concluindo. O progresso fica salvo.")

if roteiro["aviso_topo"]:
    st.warning(roteiro["aviso_topo"])

# O prefixo evita que o progresso de um roteiro se misture com o do outro.
prefixo = nome_roteiro.replace(" ", "_")

# Calcula o progresso somando só os itens do roteiro selecionado.
total_itens = sum(len(lista) for lista in roteiro["secoes"].values())
total_feitos = sum(
    1
    for chave, valor in st.session_state.estado.items()
    if chave.startswith(prefixo) and valor
)

st.progress(total_feitos / total_itens if total_itens else 0)
st.write(f"{total_feitos} de {total_itens} concluídos")

st.divider()

for secao, lista_itens in roteiro["secoes"].items():
    st.subheader(secao)
    for indice, texto in enumerate(lista_itens):
        chave = f"{prefixo}-{secao}-{indice}"
        marcado = st.session_state.estado.get(chave, False)
        novo_valor = st.checkbox(texto, value=marcado, key=chave)
        if novo_valor != marcado:
            st.session_state.estado[chave] = novo_valor
            salvar_estado(st.session_state.estado)

    if secao == "Antes do culto":
        if nome_roteiro == "PC Holyrics":
            st.info(
                "Passe a letra antes do ministro terminar a última palavra. "
                "Dica: passe quando ele começar a cantar a penúltima palavra."
            )
        if nome_roteiro == "Iluminação":
            st.info(
                "Já temos máquina de fumaça, pode usar à vontade mas com "
                "moderação."
            )
        st.info(
            "Durante o culto: foco total, evite distrações e conversas "
            "desnecessárias."
        )
        if nome_roteiro == "Iluminação":
            st.info(
                "No louvor, acompanhe a atmosfera da música e faça a "
                "iluminação como complemento da equipe de louvor. Combine "
                "com o operador do PC Arena pra usar fundo e parled da "
                "mesma cor."
            )
        st.divider()

    if secao == "Depois do culto" and nome_roteiro == "Iluminação":
        st.warning(
            "Se o operador do PC Arena não desligar os disjuntores e você "
            "for embora depois dele, a responsabilidade é sua."
        )

st.divider()

if st.button("Reiniciar checklist deste roteiro", type="secondary"):
    for chave in list(st.session_state.estado.keys()):
        if chave.startswith(prefixo):
            del st.session_state.estado[chave]
    salvar_estado(st.session_state.estado)
    st.rerun()

st.caption(
    "Tudo que vem da gestão são ordens pastorais. Primeiro execute o que foi "
    "pedido; sugestões só depois, direto com a gestão."
)
