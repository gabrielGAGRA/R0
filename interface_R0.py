import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sympy as sp
import io


def resolver_estrutura(Ha, Hd, Pbc):
    # CÁLCULOS SIMBÓLICOS E NUMÉRICOS
    # Equilíbrio Horizontal
    Fh = 0
    Hc = Fh - Ha - Hd  # ou equivalente: Hc = -Ha - Hd

    # Equilíbrio Vertical
    Fv = 0
    Abc = 3
    Vbc = Pbc * Abc  # carregamento total entre B e C
    Vb_Vc = Fv - Vbc  # ou Vb+Vc = - Vbc

    # Equilíbrio de Momentos
    Mc = 0
    Vb = (Vbc * 3 / 2 - Hd * 1 - Mc) / 3
    Vc = Vb_Vc - Vb

    # Outros cálculos
    Fh_barra = 0
    N = Fh_barra + Ha  # normal axial na barra

    Fv_barra = 0
    x = sp.Symbol("x")
    V = Fv_barra + Vb * (1 - x)  # diagrama de forças cortantes (simplificado)
    M = -sp.integrate(V, x)  # diagrama de momentos

    return Hc, Vb, Vc, N, sp.simplify(V), sp.simplify(M)


def plot_estrutura_e_equacoes(Ha, Hd, Pbc):
    # Resolver os cálculos
    Hc, Vb, Vc, N, V, M = resolver_estrutura(Ha, Hd, Pbc)

    # Definindo os valores para formatação dos textos
    texto_eq = (
        f"Equações fundamentais do equilíbrio\n\n"
        "I. Equilíbrio Horizontal\n"
        "Fh = 0\n"
        f"Hc = - Ha - Hd = {-Ha - Hd} kN\n\n"
        "II. Equilíbrio Vertical\n"
        "Fv = 0\n"
        f"Vb + Vc = - Vbc = {-Pbc*3} kN\n\n"
        "III. Equilíbrio de Momentos\n"
        "Mc = 0\n"
        f"Vb = (Vbc * 3/2 - Hd * 1 - Mc) / 3 = ({Vb} kN)\n"
        f"N = Fh_barra + Ha = ({Ha} kN)\n"
        f"V(x) = {sp.pretty(V)}  kN\n"
        f"M(x) = {sp.pretty(M)}  kN·m\n\n"
        "\n*Grau de estatisticidade da estrutura: Isostático"
    )

    # Definindo os pontos da estrutura
    A = (-1, 0)
    B = (0, 0)
    C = (3, 0)
    D = (3, 1)

    # Criar figura com dois subplots (um para a estrutura, outro para as equações)
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 9), gridspec_kw={"height_ratios": [2, 1]}
    )

    # ---------- Plot da Estrutura (ax1) ----------
    ax1.plot([A[0], B[0]], [A[1], B[1]], "k-", linewidth=2)  # A-B
    ax1.plot([B[0], C[0]], [B[1], C[1]], "k-", linewidth=2)  # B-C
    ax1.plot([C[0], D[0]], [C[1], D[1]], "k-", linewidth=2)  # C-D

    # Marcação dos nós com legenda:
    for point, label, dx, dy in zip(
        [A, B, C, D],
        ["A", "B\n(Apoio Simples)", "C\n(Apoio Articulado)", "D"],
        [-0.1, -0.05, 0.15, 0.1],
        [-0.2, 0.1, 0.1, 0.1],
    ):
        ax1.plot(point[0], point[1], "ko")
        ax1.text(point[0] + dx, point[1] + dy, label, fontsize=10, ha="center")

    # Apoio articulado em C
    ax1.add_patch(
        patches.Polygon(
            [[C[0] - 0.3, C[1] - 0.5], [C[0] + 0.3, C[1] - 0.5], [C[0], C[1]]],
            closed=True,
            fill=None,
            edgecolor="green",
        )
    )

    # Apoio Simples em B
    ax1.add_patch(
        patches.Polygon(
            [[B[0] - 0.3, B[1] - 0.5], [B[0] + 0.3, B[1] - 0.5], [B[0], B[1]]],
            closed=True,
            fill=None,
            edgecolor="blue",
        )
    )
    ax1.add_patch(
        patches.Ellipse((B[0], B[1] - 0.6), 0.2, 0.15, fill=None, edgecolor="blue")
    )

    # Força de Ha em A (horizontal)
    ax1.annotate(
        "",
        xy=(A[0] - 0.5, A[1]),
        xytext=(A[0], A[1]),
        arrowprops=dict(facecolor="red", arrowstyle="->", lw=2),
    )
    ax1.text(A[0] - 0.6, A[1] + 0.1, f"{Ha} kN", color="red")

    # Força horizontal Hd em D
    ax1.annotate(
        "",
        xy=(D[0] + 0.5, D[1]),
        xytext=(D[0], D[1]),
        arrowprops=dict(facecolor="red", arrowstyle="->", lw=2),
    )
    ax1.text(D[0] + 0.3, D[1] + 0.1, f"{-Hd} kN", color="red")

    # Carregamento distribuído entre B e C
    for i in range(4):
        x = 0.5 + i * (2.0 / 3)
        ax1.annotate(
            "",
            xy=(x, 0),  # Changed end point to y=0
            xytext=(x, 0.5),  # Start point remains at y=0.5
            arrowprops=dict(facecolor="blue", arrowstyle="->", lw=1),
        )
    ax1.text(1.5, 0.4, f"{-Pbc} kN/m\ndistribuído", ha="center", color="blue")

    ax1.set_xlim(-2, 4)
    ax1.set_ylim(-1.5, 2)
    ax1.set_aspect("equal")
    ax1.set_title("Representação Estrutural e Forças")
    ax1.grid(True)

    # ---------- Exibição das Equações (ax2) ----------
    ax2.axis("off")
    ax2.text(0, 1, texto_eq, fontsize=11, family="monospace", va="top")

    plt.tight_layout()
    return fig


# ================== STREAMLIT APP ==================
st.title("Análise Estrutural Interativa")

st.sidebar.header("Entrada de Dados")
Ha = st.sidebar.number_input("Força horizontal em A (Ha)", value=1.0, step=0.1)
Hd = st.sidebar.number_input(
    "Força vertical em D (Hd) [valor negativo se para baixo]", value=-3.0, step=0.1
)
Pbc = st.sidebar.number_input(
    "Pressão distribuída entre B e C (Pbc) [valor negativo se para baixo]",
    value=-2.0,
    step=0.1,
)

if st.sidebar.button("Gerar Análise"):
    # Gerar o gráfico com a estrutura e as equações
    fig = plot_estrutura_e_equacoes(Ha, Hd, Pbc)

    st.pyplot(fig)

    # Salvar a figura em PDF e permitir download
    pdf_bytes = io.BytesIO()
    fig.savefig(pdf_bytes, format="pdf")
    pdf_bytes.seek(0)

    st.download_button(
        label="Download do PDF",
        data=pdf_bytes,
        file_name="analise_estrutura.pdf",
        mime="application/pdf",
    )
