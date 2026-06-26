import streamlit as st
import pandas as pd
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
import io
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gerador Almirante Tamandaré", layout="wide")

# --- FUNÇÃO AUXILIAR PARA ENCONTRAR A FONTE (RESOLVE MAIÚSCULAS/MINÚSCULAS) ---
def obter_caminho_fonte():
    nome_procurado = "arbutusslab-regular.ttf"
    for arquivo in os.listdir("."):
        if arquivo.lower() == nome_procurado:
            return arquivo
    return "ArbutusSlab-Regular.ttf"

# --- FUNÇÃO 1: CERTIFICADO ALUNOS (MANTÉM ARIAL PADRÃO) ---
def gerar_certificado_no_padrao(nome_aluno, turma, coordenador, pdt, diretor, bimestre, medalha):
    packet = io.BytesIO()
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
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
    else:
        cor_rgb = (0, 51, 102)
        texto_titulo = "SUPERAÇÃO"
        frase_inicial = "Certificamos como aluno(a)"

    canv.set_font("Arial", "B", 16)
    canv.set_text_color(0, 0, 0)
    canv.set_xy(0, 48)
    canv.cell(297, 10, frase_inicial, ln=True, align="C")

    canv.set_font("Arial", "B", 36)
    canv.set_text_color(*cor_rgb)
    canv.set_xy(0, 60)
    canv.cell(297, 10, texto_titulo, ln=True, align="C")

    canv.set_font("Arial", "B", 26)
    canv.set_text_color(0, 0, 0)
    canv.set_xy(0, 74)
    canv.cell(297, 20, nome_aluno.upper(), ln=True, align="C")
    
    canv.set_font("Arial", "B", 16)
    canv.set_xy(25, 98)
    
    if medalha == "SUPERAÇÃO":
        frase = (f"Matriculado(a) na {turma.upper()}, pela notável evolução acadêmica "
                 f"e esforço demonstrado no {bimestre} do Ano Letivo de 2026, "
                 f"conseguindo avançar nos estudos de forma melhorada.")
    else:
        frase = (f"Matriculado(a) na {turma.upper()}, pela excelência acadêmica "
                 f"nos estudos no {bimestre} do Ano Letivo de 2026 da EEMTI Almirante Tamandaré, "
                 f"alcançou padrão {medalha}.")
        
    canv.multi_cell(247, 8, frase, align="C")

    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = datetime.now()
    data_extenso = f"Fortaleza, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}"
    
    canv.set_font("Arial", "", 14)
    canv.set_xy(0, 120)
    canv.cell(297, 10, data_extenso, ln=True, align="C")
    
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

# --- FUNÇÃO 2: CERTIFICADO EVENTOS GERAIS (USANDO O ARQUIVO CERTIFICADO_BANCA.PDF) ---
def gerar_certificado_evento_geral(nome_participante, nome_evento, ano, carga_horaria):
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
    arquivo_fonte = obter_caminho_fonte()
    canv.add_font("ArbutusSlab", "", arquivo_fonte, uni=True)
    
    canv.set_font("ArbutusSlab", "", 24)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(0, 75)
    canv.cell(297, 10, "Certificamos que", ln=True, align="C")
    
    canv.set_font("ArbutusSlab", "", 26)
    canv.set_text_color(212, 175, 55) 
    canv.set_xy(0, 88)
    canv.cell(297, 15, nome_participante.upper(), ln=True, align="C")
    
    canv.set_font("ArbutusSlab", "", 24)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(30, 108)
    frase = (f"Participou do evento {nome_evento.upper()} no ano de {ano} "
             f"nesta unidade de ensino, com carga horária total de {carga_horaria}h.")
    canv.multi_cell(237, 9, frase, align="C")

    temp_pdf_content = canv.output()
    
    # CORREÇÃO AQUI: Agora aponta para o nome correto do seu arquivo PDF
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


# --- INTERFACE STREAMLIT ---
st.title("🎓 Sistema de Certificação")

# Criando as 2 Abas operacionais
tab_alunos, tab_eventos = st.tabs([
    "🏆 Alunos Destaque", 
    "📅 Eventos Gerais"
])

# --- CONTEÚDO DA ABA 1: ALUNOS ---
with tab_alunos:
    with st.expander("⚙️ Configurações de Assinaturas e Critérios dos Alunos", expanded=True):
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
        if not turma_sel.strip() or not aluno_sel.strip():
            st.warning("⚠️ Por favor, preencha a Turma e o Nome do Aluno antes de gerar!")
        else:
            try:
                pdf_final = gerar_certificado_no_padrao(aluno_sel, turma_sel, nome_coord, nome_pdt, nome_diretor, bimestre_sel, padrao_sel)
                st.download_button(label=f"💾 BAIXAR PDF - {aluno_sel.upper()}", data=pdf_final, file_name=f"Certificado_{padrao_sel}_{aluno_sel.replace(' ', '_')}.pdf", mime="application/pdf")
                st.balloons()
            except Exception as e:
                st.error(f"Erro: {e}")

# --- CONTEÚDO DA ABA 2: EVENTOS GERAIS ---
with tab_eventos:
    st.subheader("Certificado de Eventos Gerais da Escola")
    
    col_ev1, col_ev2 = st.columns(2)
    with col_ev1:
        nome_part_ev = st.text_input("Nome Completo do Participante / Professor:", key="ev_part").upper()
        nome_evento_ev = st.text_input("Nome do Evento (Ex: Feira de Ciências, Gincana...):", key="ev_nome").upper()
    with col_ev2:
        anos_lista_ev = [str(a) for a in range(2026, 2032)]
        ano_sel_ev = st.selectbox("Selecione o Ano:", anos_lista_ev, key="ev_ano")
        ch_ev = st.text_input("Carga Horária (Apenas números, Ex: 4, 10, 20):", "5", key="ev_ch")

    if st.button("🚀 GERAR CERTIFICADO DE EVENTO GERAL", use_container_width=True):
        if nome_part_ev.strip() == "" or nome_evento_ev.strip() == "":
            st.warning("Por favor, preencha o nome do participante e o nome do evento.")
        else:
            try:
                pdf_evento = gerar_certificado_evento_geral(nome_part_ev, nome_evento_ev, ano_sel_ev, ch_ev)
                st.download_button(
                    label=f"💾 BAIXAR CERTIFICADO - {nome_part_ev}",
                    data=pdf_evento,
                    file_name=f"Certificado_Evento_{nome_part_ev}.pdf",
                    mime="application/pdf"
                )
                st.success(f"Certificado gerado com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao gerar certificado de evento: {e}")

# --- RODAPÉ ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; font-size: 0.9em; padding: 10px;'>
        © 2026 Certificação Tamandaré - Desenvolvido por <b>Prof. Yannka Moreira</b> e <b>Prof. Alan Ribeiro</b>
    </div>
    """, 
    unsafe_allow_html=True
)
