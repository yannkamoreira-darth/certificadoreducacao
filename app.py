import streamlit as st
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
import io
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Gerador de Certificados", layout="wide")

def gerar_certificado_no_padrao(nome_aluno, turma, coordenador, pdt, diretor, bimestre, medalha, nome_escola):
    packet = io.BytesIO()
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
    # --- DEFINIÇÃO DE CORES E TÍTULOS BASEADO NO PADRÃO ---
    if medalha == "OURO":
        cor_rgb = (212, 175, 55)   # Dourado
        texto_titulo = "ALUNO(A) DESTAQUE"
        frase_inicial = "Certificamos como"
    elif medalha == "PRATA":
        cor_rgb = (150, 150, 150)  # Prata
        texto_titulo = "ALUNO(A) DESTAQUE"
        frase_inicial = "Certificamos como"
    elif medalha == "BRONZE":
        cor_rgb = (176, 115, 67)   # Bronze
        texto_titulo = "ALUNO(A) DESTAQUE"
        frase_inicial = "Certificamos como"
    else: # SUPERAÇÃO
        cor_rgb = (0, 51, 102)     # Azul Marinho
        texto_titulo = "SUPERAÇÃO"
        frase_inicial = "Certificamos como aluno(a)"

    # --- 1. FRASE INICIAL ---
    canv.set_font("Arial", "B", 16)
    canv.set_text_color(0, 0, 0) 
    canv.set_xy(0, 48) 
    canv.cell(297, 10, frase_inicial, ln=True, align="C")

    # --- 2. TÍTULO (COR DINÂMICA) ---
    canv.set_font("Arial", "B", 36)
    canv.set_text_color(*cor_rgb) 
    canv.set_xy(0, 60) 
    canv.cell(297, 10, texto_titulo, ln=True, align="C")

    # --- 3. NOME DO ALUNO ---
    canv.set_font("Arial", "B", 26)
    canv.set_text_color(0, 0, 0)
    canv.set_xy(0, 74) 
    canv.cell(297, 20, nome_aluno.upper(), ln=True, align="C")
    
    # --- 4. FRASE DE MÉRITO (CORRIGIDA) ---
    canv.set_font("Arial", "B", 16)
    canv.set_xy(25, 98) 
    
    if medalha == "SUPERAÇÃO":
        frase = (f"matriculado(a) na turma {turma.upper()} do Ensino Médio da {nome_escola.upper()}, "
                 f"destacou-se por seu comprometimento, dedicação e evolução em cumprir as "
                 f"atividades escolares no {bimestre} do Ano Letivo de 2026, conseguindo avançar nos estudos.")
    else:
        frase = (f"matriculado(a) na turma {turma.upper()} do Ensino Médio da {nome_escola.upper()}, "
                 f"destacou-se pelo comprometimento, dedicação e excelência no cumprimento das atividades "
                 f"escolares durante o {bimestre} do Ano Letivo de 2026, alcançando o padrão {medalha}.")
        
    canv.multi_cell(247, 8, frase, align="C")

    # --- 5. DATA ---
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = datetime.now()
    data_extenso = f"Fortaleza, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}"
    
    canv.set_font("Arial", "", 14)
    canv.set_xy(0, 126) 
    canv.cell(297, 10, data_extenso, ln=True, align="C")
    
    # --- 6. LINHAS E ASSINATURAS ---
    canv.set_draw_color(0, 0, 0)
    
    # --- COORDENADOR(A) ---
    canv.line(45, 146, 125, 146) 
    canv.set_font("Arial", "B", 11)
    canv.set_xy(35, 148) 
    canv.cell(100, 5, coordenador.upper(), 0, 1, "C")
    canv.set_font("Arial", "", 10)
    canv.set_x(35)
    canv.cell(100, 4, "Coordenador(a)", 0, 0, "C")
    
    # --- PROFESSOR(A) PDT ---
    canv.line(172, 146, 252, 146)
    canv.set_font("Arial", "B", 11)
    canv.set_xy(162, 148) 
    canv.cell(100, 5, pdt.upper(), 0, 1, "C")
    canv.set_font("Arial", "", 10)
    canv.set_x(162)
    canv.cell(100, 4, "Professor(a) PDT", 0, 0, "C")

    # --- DIRETOR(A) ---
    canv.line(108.5, 171, 188.5, 171)
    canv.set_font("Arial", "B", 11)
    canv.set_xy(98.5, 173)
    canv.cell(100, 5, diretor.upper(), 0, 1, "C")
    canv.set_font("Arial", "", 10)
    canv.set_x(98.5)
    canv.cell(100, 4, "Diretor(a)", 0, 0, "C")
    
    # --- AJUSTE DA SAÍDA FPDF ---
    temp_pdf_content = canv.output(dest='S')
    if isinstance(temp_pdf_content, str):
        temp_pdf_content = temp_pdf_content.encode('latin1')
    
    if not os.path.exists("Certificado.pdf"):
        raise FileNotFoundError("Certificado.pdf não encontrado!")
        
    modelo_pdf = PdfReader(open("Certificado.pdf", "rb"))
    overlay_pdf = PdfReader(io.BytesIO(temp_pdf_content))
    output = PdfWriter()
    pagina_modelo = modelo_pdf.pages[0]
    pagina_modelo.merge_page(overlay_pdf.pages[0])
    output.add_page(pagina_modelo)
    
    final_packet = io.BytesIO()
    output.write(final_packet)
    return final_packet.getvalue()

# --- INTERFACE STREAMLIT ---
st.title("🎓 Gerador de Certificados Escolar")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configurações")
    # Retornado os valores padrão úteis para evitar digitação repetitiva
    nome_da_escola = st.text_input("Nome da Escola:", "")
    nome_coord = st.text_input("Coordenador(a):", "")
    nome_pdt = st.text_input("Professor(a) PDT:", "")
    nome_diretor = st.text_input("Diretor(a):", "")
    
    st.markdown("---")
    bimestre_sel = st.selectbox(
        "Selecione o Bimestre:",
        ["Primeiro Bimestre", "Segundo Bimestre", "Terceiro Bimestre", "Quarto Bimestre"]
    )
    
    padrao_sel = st.selectbox(
        "Selecione o Padrão:",
        ["OURO", "PRATA", "BRONZE", "SUPERAÇÃO"]
    )

    st.markdown("---")
    st.info("**📌 Critérios de Premiação:**")
    st.write("🌟 **OURO:** Média $\geq$ 9,5")
    st.write("🥈 **PRATA:** Média $\geq$ 9,0")
    st.write("🥉 **BRONZE:** Média $\geq$ 8,0")
    st.write("📈 **SUPERAÇÃO:** Evolução entre bimestres")

# Blocos de preenchimento manual do estudante
col1, col2 = st.columns([1, 2])
with col1:
    turma_sel = st.text_input("Digite a Turma (Ex: 1ª SÉRIE A):", placeholder="Ex: 3ª SÉRIE B")
with col2:
    aluno_sel = st.text_input("Digite o Nome Completo do Aluno:", placeholder="Nome do estudante")

if st.button("🚀 GERAR CERTIFICADO OFICIAL", use_container_width=True):
    if not turma_sel.strip() or not aluno_sel.strip():
        st.warning("⚠️ Por favor, preencha a Turma e o Nome do Aluno antes de gerar!")
    else:
        try:
            pdf_final = gerar_certificado_no_padrao(
                aluno_sel, turma_sel, nome_coord, nome_pdt, nome_diretor, bimestre_sel, padrao_sel, nome_da_escola
            )
            st.download_button(
                label=f"💾 BAIXAR CERTIFICADO {padrao_sel} - {aluno_sel.upper()}",
                data=pdf_final,
                file_name=f"Certificado_{padrao_sel}_{aluno_sel.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
            st.success(f"Certificado de {aluno_sel.upper()} pronto para download!")
            st.balloons()
        except Exception as e:
            st.error(f"Erro: {e}")

# --- RODAPÉ ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; font-size: 0.9em; padding: 10px;'>
        © 2026 Certificação Escolar - Desenvolvido por <b>Prof Alan Ribeiro e Prof. Yannka Moreira</b>
    </div>
    """, 
    unsafe_allow_html=True
)
