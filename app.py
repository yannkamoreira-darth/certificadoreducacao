import streamlit as st
import pandas as pd
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
import io
import os
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
# Alterado para um título genérico para servir a qualquer escola
st.set_page_config(page_title="Gerador de Certificados Escolares", layout="wide")


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================
def obter_caminho_fonte():
    """
    Procura o arquivo de fonte customizado no diretório atual,
    ignorando diferenças entre maiúsculas e minúsculas no nome do arquivo.
    """
    nome_procurado = "arbutusslab-regular.ttf"
    try:
        for arquivo in os.listdir("."):
            if arquivo.lower() == nome_procurado:
                return arquivo
    except Exception:
        pass
    return "ArbutusSlab-Regular.ttf"


# ==============================================================================
# FUNÇÃO 1: GERAR CERTIFICADO DE ALUNOS (DESTAQUE / SUPERAÇÃO)
# ==============================================================================
def gerar_certificado_no_padrao(nome_aluno, turma, coordenador, pdt, diretor, bimestre, medalha, nome_escola):
    """
    Gera o PDF do certificado de alunos usando posições fixas em milímetros.
    Recebe 'nome_escola' dinamicamente para não ficar preso a uma única instituição.
    """
    packet = io.BytesIO()
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
    # Definição das cores e títulos de acordo com a medalha
    if medalha == "OURO":
        cor_rgb = (212, 175, 55)
        texto_titulo = "ALUNO(A) DESTAQUE"
        frase_inicial = "Certificamos como"
    elif medalha == "PRATA":
        cor_rgb = (150, 150, 150)
        texto_titulo = "ALUNO(A) DESTAQUE"
        frase_inicial = "Certificamos como"
    elif medalha == "BRONZE":
        cor_rgb = (176, 115, 67)
        texto_titulo = "ALUNO(A) DESTAQUE"
        frase_inicial = "Certificamos como"
    else:  # SUPERAÇÃO
        cor_rgb = (0, 51, 102)
        texto_titulo = "SUPERAÇÃO"
        frase_inicial = "Certificamos como aluno(a)"

    # Cabeçalho do certificado
    canv.set_font("Arial", "B", 16)
    canv.set_text_color(0, 0, 0)
    canv.set_xy(0, 48)
    canv.cell(297, 10, frase_inicial, ln=True, align="C")

    # Título da Medalha/Destaque
    canv.set_font("Arial", "B", 36)
    canv.set_text_color(*cor_rgb)
    canv.set_xy(0, 60)
    canv.cell(297, 10, texto_titulo, ln=True, align="C")

    # Nome do Estudante
    canv.set_font("Arial", "B", 26)
    canv.set_text_color(0, 0, 0)
    canv.set_xy(0, 74)
    canv.cell(297, 20, nome_aluno.upper(), ln=True, align="C")
    
    # Corpo do Texto
    canv.set_font("Arial", "B", 16)
    canv.set_xy(25, 98)
    
    if medalha == "SUPERAÇÃO":
        frase = (f"Matriculado(a) na {turma.upper()}, pela notável evolução acadêmica "
                 f"e esforço demonstrado no {bimestre} do Ano Letivo de {datetime.now().year}, "
                 f"conseguindo avançar nos estudos de forma melhorada na {nome_escola.upper()}.")
    else:
        # AGORA DINÂMICO: Usa a variável nome_escola em vez do nome fixo anterior
        frase = (f"Matriculado(a) na {turma.upper()}, pela excelência acadêmica "
                 f"nos estudos no {bimestre} do Ano Letivo de {datetime.now().year} da {nome_escola.upper()}, "
                 f"alcançou padrão {medalha}.")
        
    canv.multi_cell(247, 8, frase, align="C")

    # Data Atual por extenso
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = datetime.now()
    data_extenso = f"Fortaleza, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}"
    
    canv.set_font("Arial", "", 14)
    canv.set_xy(0, 120)
    canv.cell(297, 10, data_extenso, ln=True, align="C")
    
    # Assinaturas
    canv.set_font("Arial", "B", 12)
    canv.line(45, 146, 125, 146)
    canv.set_xy(35, 148)
    canv.cell(100, 10, coordenador.upper(), 0, 0, "C")
    
    canv.line(172, 146, 252, 146)
    canv.set_xy(162, 148)
    canv.cell(100, 10, pdt.upper(), 0, 1, "C")

    canv.line(108.5, 170, 188.5, 170)
    canv.set_xy(0, 172)
    canv.cell(297, 10, diretor.upper(), 0, 1, "C")
    
    # Mesclar com o PDF modelo de fundo
    temp_pdf_content = canv.output()
    modelo_pdf = PdfReader(open("Certificado.pdf", "rb"))
    overlay_pdf = PdfReader(io.BytesIO(temp_pdf_content))
    output = PdfWriter()
    pagina_modelo = modelo_pdf.pages[0]
    pagina_modelo.merge_page(overlay_pdf.pages[0])
    output.add_page(pagina_modelo)
    
    final_packet = io.BytesIO()
    output.write(final_packet)
    return final_packet.getvalue()


# ==============================================================================
# FUNÇÃO 2: GERAR CERTIFICADO DE EVENTOS GERAIS
# ==============================================================================
def gerar_certificado_evento_geral(nome_participante, nome_evento, ano, carga_horaria, nome_escola):
    """
    Gera o PDF de eventos gerais recebendo o nome da escola dinamicamente.
    """
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
    arquivo_fonte = obter_caminho_fonte()
    
    if os.path.exists(arquivo_fonte):
        canv.add_font("ArbutusSlab", "", arquivo_fonte, uni=True)
        fonte_usada = "ArbutusSlab"
    else:
        fonte_usada = "Arial"
    
    canv.set_font(fonte_usada, "B" if fonte_usada == "Arial" else "", 24)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(0, 75)
    canv.cell(297, 10, "Certificamos que", ln=True, align="C")
    
    canv.set_font(fonte_usada, "B" if fonte_usada == "Arial" else "", 26)
    if fonte_usada == "ArbutusSlab":
        canv.set_text_color(212, 175, 55)
    else:
        canv.set_text_color(184, 134, 11)
        
    canv.set_xy(0, 88)
    canv.cell(297, 15, nome_participante.upper(), ln=True, align="C")
    
    canv.set_font(fonte_usada, "B" if fonte_usada == "Arial" else "", 24)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(30, 108)
    
    # Texto formatado dinamicamente com a escola informada no painel
    frase = (f"Participou do evento como avaliador(a) no evento {nome_evento.upper()} no ano de {ano} "
             f"na {nome_escola.upper()}, com carga horária total de {carga_horaria}h.")
    canv.multi_cell(237, 9, frase, align="C")

    temp_pdf_content = canv.output()
    
    if not os.path.exists("Certificado_banca.pdf"):
        raise FileNotFoundError("O arquivo 'Certificado_banca.pdf' não foi encontrado na raiz do projeto!")

    modelo_pdf = PdfReader(open("Certificado_banca.pdf", "rb"))
    overlay_pdf = PdfReader(io.BytesIO(temp_pdf_content))
    output = PdfWriter()
    pagina_modelo = modelo_pdf.pages[0]
    pagina_modelo.merge_page(overlay_pdf.pages[0])
    output.add_page(pagina_modelo)
    
    final_packet = io.BytesIO()
    output.write(final_packet)
    return final_packet.getvalue()


# ==============================================================================
# INTERFACE COM O USUÁRIO (STREAMLIT)
# ==============================================================================
st.title("🎓 Sistema de Certificação Escolar")

# Criando as 2 Abas operacionais
tab_alunos, tab_eventos = st.tabs([
    "🏆 Alunos Destaque", 
    "📅 Eventos Gerais"
])

# ------------------------------------------------------------------------------
# ABA 1: ALUNOS DESTAQUE
# ------------------------------------------------------------------------------
with tab_alunos:
    with st.expander("⚙️ Configurações da Escola e Assinaturas", expanded=True):
        # Campo adicionado para permitir definir a escola também no certificado do aluno
        nome_escola_aluno = st.text_input("Nome da Escola / Unidade de Ensino:", "EEMTI Almirante Tamandaré", key="cfg_escola_aluno")
        
        st.divider()
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            nome_coord = st.text_input("Coordenador(a):", "COORDENADOR(A)", key="cfg_coord")
        with col_c2:
            nome_pdt = st.text_input("Professor(a) PDT:", "NOME DO PROFESSOR(A)", key="cfg_pdt")
        with col_c3:
            nome_diretor = st.text_input("Diretor(a):", "NOME DIRETOR(A)", key="cfg_dir")
        
        st.divider()
        col_c4, col_c5 = st.columns(2)
        with col_c4:
            bimestre_sel = st.selectbox("Bimestre:", ["Primeiro Bimestre", "Segundo Bimestre", "Terceiro Bimestre", "Quarto Bimestre"], key="cfg_bim")
        with col_c5:
            padrao_sel = st.selectbox("Padrão:", ["OURO", "PRATA", "BRONZE", "SUPERAÇÃO"], key="cfg_pad")

    st.markdown("### Preenchimento Manual do Aluno")
    col1, col2 = st.columns([1, 2])
    with col1:
        turma_sel = st.text_input("Digite a Turma:", placeholder="Ex: 1ª SÉRIE A", key="turma_aluno")
    with col2:
        aluno_sel = st.text_input("Digite o Nome Completo do Aluno:", placeholder="Nome do estudante", key="nome_aluno")

    if st.button("🚀 GERAR CERTIFICADO DE ALUNO", use_container_width=True):
        if not turma_sel.strip() or not aluno_sel.strip() or not nome_escola_aluno.strip():
            st.warning("⚠️ Por favor, preencha o Nome da Escola, a Turma e o Nome do Aluno!")
        else:
            try:
                # Agora envia também o nome_escola_aluno para a função
                pdf_final = gerar_certificado_no_padrao(
                    aluno_sel, turma_sel, nome_coord, nome_pdt, nome_diretor, bimestre_sel, padrao_sel, nome_escola_aluno
                )
                st.download_button(
                    label=f"💾 BAIXAR PDF - {aluno_sel.upper()}",
                    data=pdf_final,
                    file_name=f"Certificado_{padrao_sel}_{aluno_sel.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao gerar certificado: {e}")

# ------------------------------------------------------------------------------
# ABA 2: EVENTOS GERAIS
# ------------------------------------------------------------------------------
with tab_eventos:
    st.subheader("Certificado de Eventos Gerais da Escola")
    
    nome_escola_ev = st.text_input("Nome da Unidade de Ensino / Escola:", "EEMTI Almirante Tamandaré", key="ev_escola")
    
    col_ev1, col_ev2 = st.columns(2)
    with col_ev1:
        nome_part_ev = st.text_input("Nome Completo do Participante / Professor:", key="ev_part").upper()
        nome_evento_ev = st.text_input("Nome do Evento (Ex: Feira de Ciências, Gincana...):", key="ev_nome").upper()
    with col_ev2:
        anos_lista_ev = [str(a) for a in range(2026, 2032)]
        ano_sel_ev = st.selectbox("Selecione o Ano:", anos_lista_ev, key="ev_ano")
        ch_ev = st.text_input("Carga Horária (Apenas números, Ex: 4, 10, 20):", "5", key="ev_ch")

    if st.button("🚀 GERAR CERTIFICADO DE EVENTO GERAL", use_container_width=True):
        if nome_part_ev.strip() == "" or nome_evento_ev.strip() == "" or nome_escola_ev.strip() == "":
            st.warning("Por favor, preencha todos os campos obrigatórios (Escola, Participante e Evento).")
        else:
            try:
                pdf_evento = gerar_certificado_evento_geral(nome_part_ev, nome_evento_ev, ano_sel_ev, ch_ev, nome_escola_ev)
                st.download_button(
                    label=f"💾 BAIXAR CERTIFICADO - {nome_part_ev}",
                    data=pdf_evento,
                    file_name=f"Certificado_Evento_{nome_part_ev}.pdf",
                    mime="application/pdf"
                )
                st.success("Certificado gerado com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao gerar certificado de evento: {e}")

# ------------------------------------------------------------------------------
# RODAPÉ
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; font-size: 0.9em; padding: 10px;'>
        © 2026 Gerador de Certificados - Desenvolvido por <b>Prof. Yannka Moreira</b> e <b>Prof. Alan Ribeiro</b>
    </div>
    """, 
    unsafe_allow_html=True
)
