import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sympy as sp
import io
from typing import Tuple

# Define o backend do Matplotlib para melhor compatibilidade com Streamlit
plt.switch_backend("Agg")


def resolver_estrutura(
    Ha: float, Hd: float, Pbc: float, L_bc: float, h_cd: float
) -> Tuple[float, float, float, float, sp.Expr, sp.Expr, sp.Expr]:
    """
    Resolve as reações e os esforços internos da estrutura.

    Args:
        Ha (float): Força horizontal em A (kN). Positivo para a esquerda.
        Hd (float): Força horizontal em D (kN). Positivo para a direita.
        Pbc (float): Carga distribuída em BC (kN/m). Negativo para baixo.
        L_bc (float): Comprimento do trecho BC (m).
        h_cd (float): Altura do trecho CD (m).

    Returns:
        Tuple: Contendo Hc, Vb, Vc, N, e as expressões simbólicas para V(x),
               M(x) fatorado e M(x) expandido.
    """
    # === 1. Equilíbrio de Forças Horizontais ===
    # ΣFh = 0  =>  Ha_reacao + Hc + Hd_reacao = 0
    # Considerando as forças aplicadas Ha e Hd nos sentidos dados:
    Hc = Ha - Hd

    # === 2. Equilíbrio de Forças Verticais ===
    # ΣFv = 0  =>  Vb + Vc + (Pbc * L_bc) = 0
    Vb_Vc = -Pbc * L_bc

    # === 3. Equilíbrio de Momentos (em relação ao ponto C) ===
    # ΣM_C = 0 (sentido anti-horário é positivo)
    # -Vb*L_bc - Pbc*(L_bc^2)/2 - Hd*h_cd = 0
    Vb = (-Pbc * L_bc / 2) - (Hd * h_cd / L_bc)
    Vc = Vb_Vc - Vb

    # === 4. Esforço Normal (Axial) na barra BC ===
    # N_BC = soma das forças horizontais à esquerda de uma seção em BC
    N = Ha

    # === 5. Esforços Simbólicos (Cortante e Momento) ao longo de BC ===
    x = sp.Symbol("x", real=True)
    # V(x) = Vb + integral(Pbc dx)
    V_expr = Vb + Pbc * x
    # M(x) = integral(V(x) dx)
    M_integrated = sp.integrate(V_expr, (x, 0, x))
    M_expanded = sp.expand(M_integrated)
    # Fatora a expressão para uma melhor visualização
    M_factored = sp.factor(M_integrated)

    return (
        round(Hc, 2),
        round(Vb, 2),
        round(Vc, 2),
        round(N, 2),
        V_expr,
        M_factored,
        M_expanded,
    )


def plot_estrutura_e_equacoes(
    Ha: float,
    Hd: float,
    Pbc: float,
    L_ab: float,
    L_bc: float,
    h_cd: float,
):
    """
    Plota a estrutura, as forças e as equações de equilíbrio.
    """
    # 1. Resolver a estrutura para obter os resultados
    Hc, Vb, Vc, N, V_expr, M_factored, M_expanded = resolver_estrutura(
        Ha, Hd, Pbc, L_bc, h_cd
    )

    # 2. Definir coordenadas dos nós
    A = (-L_ab, 0)
    B = (0, 0)
    C = (L_bc, 0)
    D = (L_bc, h_cd)

    # 3. Criar figura e eixos (subplots)
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 10), gridspec_kw={"height_ratios": [2, 1.2]}
    )
    plt.style.use("seaborn-v0_8-whitegrid")

    # --- Eixo 1: Desenho da Estrutura ---
    # Barras da estrutura (cinza escuro e mais espessas)
    ax1.plot([A[0], B[0]], [A[1], B[1]], color="#404040", linewidth=4, zorder=1)
    ax1.plot([B[0], C[0]], [B[1], C[1]], color="#404040", linewidth=4, zorder=1)
    ax1.plot([C[0], D[0]], [C[1], D[1]], color="#404040", linewidth=4, zorder=1)

    # Nós da estrutura (pontos pretos sobre as barras)
    for point, label in zip([A, B, C, D], ["A", "B", "C", "D"]):
        ax1.plot(point[0], point[1], "ko", markersize=8, zorder=10)
        ax1.text(point[0], point[1] + 0.2, label, fontsize=12, ha="center", va="bottom")

    # Apoio Articulado em C (sólido)
    tri_c = patches.Polygon(
        [[C[0] - 0.25, C[1] - 0.4], [C[0] + 0.25, C[1] - 0.4], [C[0], C[1]]],
        closed=True,
        fill=True,
        facecolor="darkgreen",
        edgecolor="black",
        zorder=5,
    )
    ax1.add_patch(tri_c)
    ax1.plot([C[0] - 0.3, C[0] + 0.3], [C[1] - 0.4, C[1] - 0.4], "k-", lw=1)
    ax1.text(C[0], C[1] - 0.5, "Apoio Articulado", ha="center", va="top")

    # Apoio Simples (de rolete) em B (sólido)
    tri_b = patches.Polygon(
        [[B[0] - 0.25, B[1] - 0.4], [B[0] + 0.25, B[1] - 0.4], [B[0], B[1]]],
        closed=True,
        fill=True,
        facecolor="darkblue",
        edgecolor="black",
        zorder=5,
    )
    ax1.add_patch(tri_b)
    roller1 = patches.Circle((B[0] - 0.1, B[1] - 0.5), radius=0.08, color="darkblue")
    roller2 = patches.Circle((B[0] + 0.1, B[1] - 0.5), radius=0.08, color="darkblue")
    ax1.add_patch(roller1)
    ax1.add_patch(roller2)
    ax1.plot([B[0] - 0.3, B[0] + 0.3], [B[1] - 0.58, B[1] - 0.58], "k-", lw=1)
    ax1.text(B[0], B[1] - 0.68, "Apoio Simples", ha="center", va="top")

    # Forças Aplicadas (setas)
    # Força Ha em A
    ax1.annotate(
        "",
        xy=(A[0] - 0.5, A[1]),
        xytext=(A[0], A[1]),
        arrowprops=dict(facecolor="red", shrink=0.05, width=2, headwidth=8),
        zorder=11,
    )
    ax1.text(A[0] - 0.6, A[1] + 0.1, f"{Ha:.2f} kN", color="red", ha="right")

    # Força Hd em D
    hd_mag = abs(Hd)
    x_start, x_end = (D[0], D[0] + 0.5) if Hd >= 0 else (D[0], D[0] - 0.5)
    ax1.annotate(
        "",
        xy=(x_end, D[1]),
        xytext=(x_start, D[1]),
        arrowprops=dict(facecolor="red", shrink=0.05, width=2, headwidth=8),
        zorder=11,
    )
    ax1.text(
        x_end + (0.1 if Hd >= 0 else -0.1),
        D[1],
        f"{hd_mag:.2f} kN",
        color="red",
        ha="left" if Hd >= 0 else "right",
        va="center",
    )

    # Carga Distribuída Pbc
    num_arrows = 5
    for i in range(num_arrows):
        x_pos = (i + 1) * (L_bc / (num_arrows + 1))
        ax1.annotate(
            "",
            xy=(x_pos, 0),
            xytext=(x_pos, 0.6),
            arrowprops=dict(facecolor="royalblue", shrink=0.05, width=1, headwidth=6),
            zorder=2,
        )
    ax1.plot([0, L_bc], [0.6, 0.6], "--", color="royalblue")
    ax1.text(
        L_bc / 2,
        0.7,
        f"{abs(Pbc):.2f} kN/m",
        ha="center",
        va="bottom",
        color="royalblue",
    )

    # Configurações do plot da estrutura
    ax1.set_xlim(-L_ab - 1, L_bc + 1)
    ax1.set_ylim(-1.5, h_cd + 1.5)
    ax1.set_aspect("equal", adjustable="box")
    ax1.set_title("Representação Estrutural e Forças", fontsize=16, fontweight="bold")
    ax1.set_xlabel("Distância (m)")
    ax1.set_ylabel("Altura (m)")

    # --- Eixo 2: Exibição das Equações ---
    ax2.axis("off")

    # Converte expressões Sympy para strings LaTeX
    V_latex = sp.latex(sp.N(V_expr, 2), mul_symbol="dot")
    M_factored_latex = sp.latex(sp.N(M_factored, 2), mul_symbol="dot")
    M_expanded_latex = sp.latex(sp.N(M_expanded, 2), mul_symbol="dot")

    # Formata os valores numéricos
    Hc_val = f"{Hc:.2f}"
    sum_V_val = f"{-Pbc * L_bc:.2f}"
    Vb_val = f"{Vb:.2f}"
    N_val = f"{N:.2f}"

    # String LaTeX com as equações alinhadas
    eq_text = (
        r"\begin{align*}"
        r"\mathbf{Equilíbrio\;de\;Forças\;e\;Momentos:}& \\"
        r"\sum F_H = 0 \implies H_C &= H_A - H_D = \mathbf{{{Hc_val}\;kN}} \\"
        r"\sum F_V = 0 \implies V_B + V_C &= -(P_{{bc}} \cdot L_{{bc}}) = \mathbf{{{sum_V_val}\;kN}} \\"
        r"\sum M_C = 0 \implies V_B &= \frac{{-P_{{bc}} \cdot L_{{bc}}/2 - H_D \cdot h_{{cd}}}}{{L_{{bc}}}} = \mathbf{{{Vb_val}\;kN}} \\"
        r"N_{{BC}} &= H_A = \mathbf{{{N_val}\;kN}} \\"
        r"\\ \mathbf{Esforços\;na\;Barra\;BC:}& \\"
        r"V(x) &= V_B + P_{{bc}} \cdot x = \mathbf{{{V_latex}\;kN}} \\"
        r"M(x) &= \int V(x) dx = \mathbf{{{M_factored_latex}}} \\"
        r"M(x) &= \mathbf{{{M_expanded_latex}\;kN \cdot m}}"
        r"\end{align*}"
    ).format(
        Hc_val=Hc_val,
        sum_V_val=sum_V_val,
        Vb_val=Vb_val,
        N_val=N_val,
        V_latex=V_latex,
        M_factored_latex=M_factored_latex,
        M_expanded_latex=M_expanded_latex,
    )

    ax2.text(0.5, 0.95, eq_text, fontsize=14, family="serif", ha="center", va="top")

    # Texto de Grau de Estaticidade com separador
    ax2.axhline(0.1, color="gray", linestyle="--", linewidth=1)
    ax2.text(
        0.5,
        0.05,
        "Grau de Estatisticidade: Isostático",
        fontsize=12,
        family="serif",
        fontstyle="italic",
        ha="center",
        va="bottom",
    )

    fig.tight_layout(pad=2.0)
    return fig


# ================== INTERFACE STREAMLIT ==================

st.set_page_config(layout="wide")
st.title("Análise Estrutural 2D Parametrizada")

st.sidebar.header("Parâmetros de Entrada")
st.sidebar.info(
    "Ajuste as forças e dimensões da estrutura. Os valores padrão "
    "correspondem ao problema da imagem fornecida."
)

# --- Entradas do Usuário ---
with st.sidebar.expander("**Forças Aplicadas**", expanded=True):
    Ha = st.number_input(
        "Força horizontal em A (Ha) [kN] (positivo → esquerda)",
        value=1.0,
        step=0.1,
        format="%.2f",
    )
    Hd = st.number_input(
        "Força horizontal em D (Hd) [kN] (positivo → direita)",
        value=3.0,
        step=0.1,
        format="%.2f",
    )
    Pbc = st.number_input(
        "Carga distribuída em BC (Pbc) [kN/m] (negativo → baixo)",
        value=-2.0,
        step=0.1,
        format="%.2f",
    )

with st.sidebar.expander("**Dimensões da Estrutura**", expanded=True):
    L_ab = st.number_input(
        "Comprimento AB (L_ab) [m]", value=1.0, step=0.1, min_value=0.1, format="%.2f"
    )
    L_bc = st.number_input(
        "Comprimento BC (L_bc) [m]", value=3.0, step=0.1, min_value=0.1, format="%.2f"
    )
    h_cd = st.number_input(
        "Altura CD (h_cd) [m]", value=1.0, step=0.1, min_value=0.1, format="%.2f"
    )

# --- Lógica Principal da Aplicação ---
col1, col2 = st.columns([0.6, 0.4])

with col1:
    st.subheader("Visualização da Estrutura e Equacionamento")
    with st.spinner("Calculando e gerando a visualização..."):
        fig = plot_estrutura_e_equacoes(Ha, Hd, Pbc, L_ab, L_bc, h_cd)
        st.pyplot(fig)

        # Funcionalidade de Download da Imagem
        png_bytes = io.BytesIO()
        fig.savefig(png_bytes, format="png", dpi=300, bbox_inches="tight")
        png_bytes.seek(0)

        st.download_button(
            label="📥 Download da Análise (PNG)",
            data=png_bytes,
            file_name=f"analise_estrutural_Ha{Ha}_Hd{Hd}.png",
            mime="image/png",
        )

with col2:
    st.subheader("Resumo dos Resultados")
    # Recalcula para exibir os resultados textuais
    Hc, Vb, Vc, N, V_expr, M_factored, M_expanded = resolver_estrutura(
        Ha, Hd, Pbc, L_bc, h_cd
    )

    st.metric(label="Reação Horizontal em C (Hc)", value=f"{Hc:.2f} kN")
    st.metric(label="Reação Vertical em B (Vb)", value=f"{Vb:.2f} kN")
    st.metric(label="Reação Vertical em C (Vc)", value=f"{Vc:.2f} kN")
    st.metric(label="Esforço Normal em BC (N)", value=f"{N:.2f} kN")

    st.markdown("---")
    st.markdown("**Expressões de Esforços em BC (para $0 \\le x \\le L_{bc}$):**")

    st.latex(f"V(x) = {sp.latex(sp.N(V_expr, 2), mul_symbol='dot')}")
    st.latex(f"M(x) = {sp.latex(sp.N(M_expanded, 2), mul_symbol='dot')}")
