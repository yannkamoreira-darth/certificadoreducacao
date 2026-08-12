import streamlit as st
import pandas as pd
from fpdf import FPDF
from pypdf import PdfReader, PdfWriter
import io
import os
import tempfile
from datetime import datetime

# Configuração da página da aplicação
st.set_page_config(page_title="Gerador Multiescolas de Certificados", layout="wide")

# ==========================================
# BARRA LATERAL (SIDEBAR): CONFIGURAÇÕES DA ESCOLA
# ==========================================
st.sidebar.header("🏫 Configuração da Escola")

# Upload da Logo da Escola
logo_escola = st.sidebar.file_uploader(
    "Upload da Logo da Escola (PNG ou JPG):", 
    type=["png", "jpg", "jpeg"],
    help="A logo será inserida no canto superior esquerdo de todos os certificados gerados."
)

# Mensagem orientativa sobre a transparência do fundo
st.sidebar.info(
    "💡 **Dica importante:** Para um melhor resultado visual no certificado, "
    "certifique-se de remover o fundo da imagem (deixando-a transparente no formato PNG) "
    "antes de fazer o upload."
)

# Exibição de prévia da logo
if logo_escola is not None:
    st.sidebar.image(logo_escola, caption="Prévia da Logo", width=120)

# Menu para ajuste de posição e dimensão da logo no PDF
with st.sidebar.expander("📐 Ajuste Fino da Logo no PDF", expanded=False):
    pos_x = st.number_input("Posição X (Horizontal mm):", value=12, min_value=0, max_value=200, help="Menor valor move para a esquerda.")
    pos_y = st.number_input("Posição Y (Vertical mm):", value=12, min_value=0, max_value=200, help="Menor valor move para o topo.")
    largura_w = st.number_input("Largura da Logo (mm):", value=25, min_value=5, max_value=100, help="Tamanho da imagem.")


# ==========================================
# FUNÇÕES DE GERAÇÃO DE PDFS (OVERLAY FPDF + PYPDF)
# ==========================================

# --- FUNÇÃO 1: CERTIFICADO ALUNOS DESTAQUE ---
def gerar_certificado_no_padrao(nome_aluno, turma, coordenador, pdt, diretor, bimestre, medalha, arquivo_logo=None, lx=12, ly=12, lw=25):
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
    if arquivo_logo is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(arquivo_logo.getvalue())
            caminho_logo_temp = temp_file.name
        canv.image(caminho_logo_temp, x=lx, y=ly, w=lw)
        os.unlink(caminho_logo_temp)

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
                 f"e esforço demonstrado no {bimestre} do Ano Letivo de 2026, "
                 f"conseguindo avançar nos estudos de forma melhorada.")
    else:
        frase = (f"Matriculado(a) na {turma.upper()}, pela excelência acadêmica "
                 f"nos estudos no {bimestre} do Ano Letivo de 2026, "
                 f"alcançou padrão {medalha}.")
        
    canv.multi_cell(247, 8, frase, align="C")

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
    
    pdf_bytes = bytes(canv.output())
    arquivo_modelo = "Certificado.pdf"
    
    if not os.path.exists(arquivo_modelo):
        raise FileNotFoundError(f"O arquivo '{arquivo_modelo}' não foi encontrado!")

    try:
        with open(arquivo_modelo, "rb") as f_modelo:
            modelo_pdf = PdfReader(f_modelo)
            overlay_pdf = PdfReader(io.BytesIO(pdf_bytes))
            output = PdfWriter()
            pagina_modelo = modelo_pdf.pages[0]
            pagina_modelo.merge_page(overlay_pdf.pages[0])
            output.add_page(pagina_modelo)
            
            final_packet = io.BytesIO()
            output.write(final_packet)
            return final_packet.getvalue()
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo '{arquivo_modelo}'. O arquivo pode estar corrompido no repositório. Detalhes: {e}")


# --- FUNÇÃO 2: CERTIFICADO EVENTOS GERAIS ---
def gerar_certificado_evento_geral(nome_participante, nome_evento, ano, carga_horaria, arquivo_logo=None, lx=12, ly=12, lw=25):
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
    if arquivo_logo is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(arquivo_logo.getvalue())
            caminho_logo_temp = temp_file.name
        canv.image(caminho_logo_temp, x=lx, y=ly, w=lw)
        os.unlink(caminho_logo_temp)
    
    if os.path.exists("ArbutusSlab-Regular.ttf"):
        canv.add_font("ArbutusSlab", "", "ArbutusSlab-Regular.ttf", uni=True)
        fonte_usada = "ArbutusSlab"
    else:
        fonte_usada = "Arial"
    
    canv.set_font(fonte_usada, "", 24)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(0, 75)
    canv.cell(297, 10, "Certificamos que", ln=True, align="C")
    
    canv.set_font(fonte_usada, "", 26)
    canv.set_text_color(212, 175, 55) 
    canv.set_xy(0, 88)
    canv.cell(297, 15, nome_participante.upper(), ln=True, align="C")
    
    canv.set_font(fonte_usada, "", 24)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(30, 108)
    frase = (f"Participou do evento {nome_evento.upper()} no ano de {ano} "
             f"nesta unidade de ensino, com carga horária total de {carga_horaria}h.")
    canv.multi_cell(237, 9, frase, align="C")

    pdf_bytes = bytes(canv.output())
    arquivo_modelo = "Certificado_Eventos.pdf"
    
    if not os.path.exists(arquivo_modelo):
        raise FileNotFoundError(f"O arquivo '{arquivo_modelo}' não foi encontrado!")

    try:
        with open(arquivo_modelo, "rb") as f_modelo:
            modelo_pdf = PdfReader(f_modelo)
            overlay_pdf = PdfReader(io.BytesIO(pdf_bytes))
            output = PdfWriter()
            pagina_modelo = modelo_pdf.pages[0]
            pagina_modelo.merge_page(overlay_pdf.pages[0])
            output.add_page(pagina_modelo)
            
            final_packet = io.BytesIO()
            output.write(final_packet)
            return final_packet.getvalue()
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo '{arquivo_modelo}'. Detalhes: {e}")


# --- FUNÇÃO 3: CERTIFICADO ALUNOS MONITORES ---
def gerar_certificado_monitor(nome_monitor, turma, nome_evento, ano, carga_horaria, arquivo_logo=None, lx=12, ly=12, lw=25):
    canv = FPDF(orientation="L", unit="mm", format="A4")
    canv.add_page()
    
    if arquivo_logo is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            temp_file.write(arquivo_logo.getvalue())
            caminho_logo_temp = temp_file.name
        canv.image(caminho_logo_temp, x=lx, y=ly, w=lw)
        os.unlink(caminho_logo_temp)
    
    if os.path.exists("ArbutusSlab-Regular.ttf"):
        canv.add_font("ArbutusSlab", "", "ArbutusSlab-Regular.ttf", uni=True)
        fonte_usada = "ArbutusSlab"
    else:
        fonte_usada = "Arial"
    
    # Cabeçalho
    canv.set_font(fonte_usada, "", 22)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(0, 68)
    canv.cell(297, 10, "Certificamos que o(a) aluno(a)", ln=True, align="C")
    
    # Nome do Monitor
    canv.set_font(fonte_usada, "", 26)
    canv.set_text_color(212, 175, 55) 
    canv.set_xy(0, 80)
    canv.cell(297, 15, nome_monitor.upper(), ln=True, align="C")
    
    # Texto descritivo da Monitoria
    canv.set_font(fonte_usada, "", 20)
    canv.set_text_color(0, 51, 102) 
    canv.set_xy(25, 100)
    
    frase = (f"Matriculado(a) na turma {turma.upper()}, atuou com excelência como "
             f"ALUNO(A) MONITOR(A) no evento {nome_evento.upper()} durante o ano letivo de {ano}, "
             f"cumprindo carga horária total de {carga_horaria} horas.")
    canv.multi_cell(247, 9, frase, align="C")

    # Data
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", 
             "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    hoje = datetime.now()
    data_extenso = f"Fortaleza, {hoje.day} de {meses[hoje.month - 1]} de {hoje.year}"
    
    canv.set_font("Arial", "", 13)
    canv.set_xy(0, 138)
    canv.cell(297, 10, data_extenso, ln=True, align="C")

    pdf_bytes = bytes(canv.output())
    
    # Lógica de seleção do modelo de fundo
    if os.path.exists("Certificado_Monitor.pdf"):
        arquivo_modelo = "Certificado_Monitor.pdf"
    elif os.path.exists("Certificado_Eventos.pdf"):
        arquivo_modelo = "Certificado_Eventos.pdf"
    elif os.path.exists("Certificado.pdf"):
        arquivo_modelo = "Certificado.pdf"
    else:
        raise FileNotFoundError("Nenhum arquivo de modelo PDF foi encontrado no repositório!")

    try:
        with open(arquivo_modelo, "rb") as f_modelo:
            modelo_pdf = PdfReader(f_modelo)
            overlay_pdf = PdfReader(io.BytesIO(pdf_bytes))
            output = PdfWriter()
            pagina_modelo = modelo_pdf.pages[0]
            pagina_modelo.merge_page(overlay_pdf.pages[0])
            output.add_page(pagina_modelo)
            
            final_packet = io.BytesIO()
            output.write(final_packet)
            return final_packet.getvalue()
    except Exception as e:
        raise Exception(
            f"O modelo '{arquivo_modelo}' está corrompido no GitHub. "
            f"Por favor, reenvie o arquivo '{arquivo_modelo}' no repositório. Detalhes: {e}"
        )


# ==========================================
# INTERFACE DO USUÁRIO (STREAMLIT)
# ==========================================
st.title("🎓 Sistema Multiescolas de Certificação")

tab_alunos, tab_eventos, tab_monitores = st.tabs([
    "🏆 Alunos Destaque", 
    "📅 Eventos Gerais",
    "🤝 Alunos Monitores"
])

# --- ABA 1: ALUNOS DESTAQUE ---
with tab_alunos:
    with st.expander("⚙️ Configurações de Assinaturas e Critérios dos Alunos", expanded=True):
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            nome_coord = st.text_input("Coordenador(a):", "COORDENADORA", key="cfg_coord")
        with col_c2:
            nome_pdt = st.text_input("Professor(a) PDT:", "NOME DO PROFESSOR(A)", key="cfg_pdt")
        with col_c3:
            nome_diretor = st.text_input("Diretor(a):", "NOME DO DIRETOR(A)", key="cfg_dir")
        
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
                pdf_final = gerar_certificado_no_padrao(
                    aluno_sel, turma_sel, nome_coord, nome_pdt, nome_diretor, 
                    bimestre_sel, padrao_sel, arquivo_logo=logo_escola,
                    lx=pos_x, ly=pos_y, lw=largura_w
                )
                st.download_button(
                    label=f"💾 BAIXAR PDF - {aluno_sel.upper()}", 
                    data=pdf_final, 
                    file_name=f"Certificado_{padrao_sel}_{aluno_sel.replace(' ', '_')}.pdf", 
                    mime="application/pdf"
                )
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao gerar certificado de aluno: {e}")

# --- ABA 2: EVENTOS GERAIS ---
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
                pdf_evento = gerar_certificado_evento_geral(
                    nome_part_ev, nome_evento_ev, ano_sel_ev, ch_ev, arquivo_logo=logo_escola,
                    lx=pos_x, ly=pos_y, lw=largura_w
                )
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

# --- ABA 3: ALUNOS MONITORES ---
with tab_monitores:
    st.subheader("Certificado de Aluno Monitor")
    
    col_mon1, col_mon2 = st.columns(2)
    with col_mon1:
        nome_monitor_in = st.text_input("Nome Completo do Aluno Monitor:", key="mon_nome").upper()
        turma_monitor_in = st.text_input("Turma do Monitor (Ex: 2ª SÉRIE B):", key="mon_turma").upper()
    with col_mon2:
        nome_evento_mon_in = st.text_input("Nome do Evento / Projeto da Monitoria:", key="mon_evento").upper()
        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            anos_mon = [str(a) for a in range(2026, 2032)]
            ano_mon_in = st.selectbox("Ano Letivo:", anos_mon, key="mon_ano")
        with col_sub2:
            ch_mon_in = st.text_input("Carga Horária (Horas):", "20", key="mon_ch")

    if st.button("🚀 GERAR CERTIFICADO DE MONITOR", use_container_width=True):
        if not nome_monitor_in.strip() or not turma_monitor_in.strip() or not nome_evento_mon_in.strip():
            st.warning("⚠️ Por favor, preencha o Nome do Monitor, a Turma e o Evento antes de gerar!")
        else:
            try:
                pdf_monitor = gerar_certificado_monitor(
                    nome_monitor_in, turma_monitor_in, nome_evento_mon_in, 
                    ano_mon_in, ch_mon_in, arquivo_logo=logo_escola,
                    lx=pos_x, ly=pos_y, lw=largura_w
                )
                st.download_button(
                    label=f"💾 BAIXAR CERTIFICADO - {nome_monitor_in}",
                    data=pdf_monitor,
                    file_name=f"Certificado_Monitor_{nome_monitor_in.replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
                st.success("Certificado de monitoria gerado com sucesso!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao gerar certificado de monitoria: {e}")

# --- RODAPÉ ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666; font-size: 0.9em; padding: 10px;'>
        © 2026 Sistema Multiescolas de Certificação - Desenvolvido por <b>Prof. Yannka Moreira</b> e <b>Prof. Alan Ribeiro</b>
    </div>
    """, 
    unsafe_allow_html=True
)
