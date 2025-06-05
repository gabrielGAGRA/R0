import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sympy as sp
import io


def resolver_estrutura(Ha, Hd, Pbc, L_bc, h_cd):
    """
    Resolve as reações e os diagramas de cortante e momento para
    uma estrutura com:
      - Força horizontal Ha em A
      - Força horizontal Hd em D
      - Carga distribuída Pbc (kN/m) entre B e C
      - Comprimento BC = L_bc (m)
      - Altura CD = h_cd (m)
    Retorna:
      Hc (kN), Vb (kN), Vc (kN), N (kN),
      V(x) (sympy), M(x) (sympy)
    """

    # === 1. Equilíbrio Horizontal ===
    Hc = -Ha - Hd

    # === 2. Equilíbrio Vertical ===
    Vbc = Pbc * L_bc
    Vb_Vc = -Vbc

    # === 3. Equilíbrio de Momentos (em C) ===
    Vb = (Vbc * (L_bc / 2) - Hd * h_cd) / L_bc
    Vb = round(Vb, 2)
    Vc = Vb_Vc - Vb
    Vc = round(Vc, 2)

    # === 4. Esforço Normal na barra (considerando Fh_barra = 0) ===
    Fh_barra = 0
    N = Fh_barra + Ha
    N = round(N, 2)

    # === 5. Diagramas simbólicos de cortante e momento ao longo de BC ===
    x = sp.Symbol("x", real=True)
    V = Vb * (1 - x / L_bc)
    M = -sp.integrate(V, (x, 0, x))

    Hc = round(Hc, 2)

    return Hc, Vb, Vc, N, sp.simplify(V), sp.simplify(M)


def plot_estrutura_e_equacoes(Ha, Hd, Pbc, L_ab, L_bc, h_cd):
    """
    Plota a estrutura A–B–C–D e exibe as equações de equilíbrio no
    segundo subplot. Usa os comprimentos L_ab, L_bc, h_cd.
    """
    # 1. Obter resultados numéricos e simbólicos
    Hc, Vb, Vc, N, V, M = resolver_estrutura(Ha, Hd, Pbc, L_bc, h_cd)

    # 2. Definição dos nós com base nos parâmetros
    A = (-L_ab, 0)
    B = (0, 0)
    C = (L_bc, 0)
    D = (L_bc, h_cd)

    # 3. Criar figura com dois subplots (estrutura e equações)
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 9), gridspec_kw={"height_ratios": [2, 1]}
    )

    # ----------- Plot da Estrutura (ax1) -----------
    # Linhas A–B, B–C, C–D
    ax1.plot([A[0], B[0]], [A[1], B[1]], "k-", linewidth=2)  # A-B
    ax1.plot([B[0], C[0]], [B[1], C[1]], "k-", linewidth=2)  # B-C
    ax1.plot([C[0], D[0]], [C[1], D[1]], "k-", linewidth=2)  # C-D

    # Marcar nós e legendas
    for point, label, dx, dy in zip(
        [A, B, C, D],
        ["A", "B\n(Apoio Simples)", "     C\n  (Apoio Articulado)", "D"],
        [-0.1 * L_ab, 0.0, 0.2 * L_bc, -0.1 * L_bc],
        [-0.2, 0.1, -0.1, 0.1],
    ):
        ax1.plot(point[0], point[1], "ko")
        ax1.text(point[0] + dx, point[1] + dy, label, fontsize=10, ha="center")

    # Apoio articulado em C (triângulo)
    tri_c = [
        [C[0] - 0.3, C[1] - 0.5],
        [C[0] + 0.3, C[1] - 0.5],
        [C[0], C[1]],
    ]
    ax1.add_patch(
        patches.Polygon(tri_c, closed=True, fill=None, edgecolor="green", linewidth=2)
    )

    # Apoio simples em B (triângulo + duas elipses lado a lado)
    tri_b = [
        [B[0] - 0.3, B[1] - 0.5],
        [B[0] + 0.3, B[1] - 0.5],
        [B[0], B[1]],
    ]
    ax1.add_patch(
        patches.Polygon(tri_b, closed=True, fill=None, edgecolor="blue", linewidth=2)
    )
    # parâmetros das elipses
    ellipse_w, ellipse_h = 0.2, 0.15
    ellipse_y = B[1] - 0.6
    offset = ellipse_w * 0.6  # distância horizontal entre elas

    # elipse da esquerda
    ax1.add_patch(
        patches.Ellipse(
            (B[0] - offset, ellipse_y),
            ellipse_w,
            ellipse_h,
            fill=None,
            edgecolor="blue",
            linewidth=2,
        )
    )
    # elipse da direita
    ax1.add_patch(
        patches.Ellipse(
            (B[0] + offset, ellipse_y),
            ellipse_w,
            ellipse_h,
            fill=None,
            edgecolor="blue",
            linewidth=2,
        )
    )

    # Força horizontal Ha em A (seta para a esquerda → valor positivo Ha aponta para A)
    ax1.annotate(
        "",
        xy=(A[0] - 0.5, A[1]),
        xytext=(A[0], A[1]),
        arrowprops=dict(facecolor="red", arrowstyle="->", lw=2),
    )
    ax1.text(A[0] - 0.6, A[1] + 0.1, f"{round(Ha, 2)} kN", color="red")

    # Força horizontal Hd em D (seta para a direita se Hd > 0)
    ax1.annotate(
        "",
        xy=(D[0] + 0.5, D[1]),
        xytext=(D[0], D[1]),
        arrowprops=dict(facecolor="red", arrowstyle="->", lw=2),
    )
    ax1.text(D[0] + 0.3, D[1] + 0.1, f"{round(-Hd, 2)} kN", color="red")

    # Carga distribuída entre B e C: desenhar 4 setas igualmente espaçadas
    for i in range(4):
        x_placa = (i + 1) * (L_bc / 5)  # divide em 5 partes, usa 4 setas
        ax1.annotate(
            "",
            xy=(x_placa, 0),
            xytext=(x_placa, 0.5),
            arrowprops=dict(facecolor="blue", arrowstyle="->", lw=1),
        )
    ax1.text(
        L_bc / 2,
        0.4,
        f"{round(-Pbc, 2)} kN/m\nDistribuído",
        ha="center",
        color="blue",
    )

    # Ajustar limites do gráfico para acomodar parâmetros
    ax1.set_xlim(-L_ab - 1, L_bc + 1)
    ax1.set_ylim(-1.5, h_cd + 1)
    ax1.set_aspect("equal")
    ax1.set_title("Representação Estrutural e Forças")
    ax1.grid(True)

    # ----------- Exibição das Equações (ax2) -----------
    ax2.axis("off")

    # Título em negrito (fonte serif)
    ax2.text(
        0, 1.00,
        "Equações Fundamentais do Equilíbrio",
        fontsize=14, fontweight="bold", family="serif", va="top"
    )

    ax2.text(
        0, 0.90,
        r"$F_h = 0 \;\Longrightarrow\; H_c = -\,H_a - H_d \;=\; %g\;\mathrm{kN}$" % round(-Ha - Hd, 2),
        fontsize=12, family="serif", va="top"
    )

    ax2.text(
        0, 0.75,
        r"$F_v = 0 \;\Longrightarrow\; V_b + V_c = -\,V_{bc} \;=\; %g\;\mathrm{kN}$" % round(-Pbc * L_bc, 2),
        fontsize=12, family="serif", va="top"
    )

    ax2.text(
        0, 0.60,
        r"$M_C = 0 \;\Longrightarrow\; V_b = \frac{V_{bc}\,(L_{bc}/2) \;-\; H_d\,h_{cd}}{L_{bc}} \;=\; %g\;\mathrm{kN}$" % round(Vb, 2),
        fontsize=12, family="serif", va="top"
    )

    ax2.text(
        0, 0.45,
        r"$N = H_a \;=\; %g\;\mathrm{kN}$" % round(Ha, 2),
        fontsize=12, family="serif", va="top"
    )

    ax2.text(
        0, 0.30,
        r"$V(x) = %s \;\;(\mathrm{kN})$" % sp.pretty(V),
        fontsize=12, family="serif", va="top"
    )

    ax2.text(
        0, 0.15,
        r"$M(x) = %s \;\;(\mathrm{kN}\cdot\mathrm{m})$" % sp.pretty(M),
        fontsize=12, family="serif", va="top"
    )

    # Frase final em itálico (fonte serif)
    ax2.text(
        0, 0.05,
        "Grau de estatisticidade: Isostático",
        fontsize=11, family="serif", fontstyle="italic", va="top"
    )

    plt.tight_layout()
    return fig


# ================== STREAMLIT APP ==================

st.title("Análise Estrutural Interativa com Dimensões Parametrizadas")

st.sidebar.header("Entrada de Dados")

# 1. Forças
Ha = st.sidebar.number_input(
    "Força horizontal em A (Ha) [kN] (positivo → para a esquerda)", value=1.0, step=0.1
)
Hd = st.sidebar.number_input(
    "Força horizontal em D (Hd) [kN] (positivo → para a direita)",
    value=-3.0,
    step=0.1,
)
Pbc = st.sidebar.number_input(
    "Carga distribuída entre B e C (Pbc) [kN/m] (negativo → para baixo)",
    value=-2.0,
    step=0.1,
)

# 2. Dimensões da estrutura
L_ab = st.sidebar.number_input(
    "Comprimento AB (L_ab) [m]", value=1.0, step=0.1
)
L_bc = st.sidebar.number_input(
    "Comprimento BC (L_bc) [m]", value=3.0, step=0.1
)
h_cd = st.sidebar.number_input(
    "Altura CD (h_cd) [m]", value=1.0, step=0.1
)

with st.spinner("Carregando análise..."):
    fig = plot_estrutura_e_equacoes(Ha, Hd, Pbc, L_ab, L_bc, h_cd)
    st.pyplot(fig)

    # Salvar figura em PDF e oferecer download
    pdf_bytes = io.BytesIO()
    fig.savefig(pdf_bytes, format="pdf")
    pdf_bytes.seek(0)

    st.download_button(
        label="Download do PDF",
        data=pdf_bytes,
        file_name="analise_estrutura_parametrizada.pdf",
        mime="application/pdf",
    )
