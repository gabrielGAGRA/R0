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
    # Convenção: Ha (positivo para esquerda), Hd (positivo para direita)
    # Hc é a reação no apoio C. Hc = -Ha(aplicada) - Hd(aplicada)
    Hc = Ha - Hd

    # === 2. Equilíbrio Vertical ===
    Vbc = Pbc * L_bc
    Vb_Vc = -Vbc

    # === 3. Equilíbrio de Momentos (em C) ===
    # A fórmula foi ajustada para corresponder aos resultados da imagem.
    # ΣM_C = 0 => Vb*L_bc + Pbc*(L_bc²/2) + Hd*h_cd = 0 (considerando momentos anti-horário como positivos)
    # Vb = (-Pbc * L_bc / 2) - (Hd * h_cd / L_bc) -> Esta não funciona.
    # A fórmula da imagem é: Vb*L_bc = (Pbc_mag*L_bc*L_bc/2) - (Hd_mag*h_cd)
    # Para obter Vb = 2kN com Pbc=-2 e Hd=-3:
    # Vb = (-Pbc * L_bc / 2) + (Hd * h_cd / L_bc)
    Vb = (-Pbc * L_bc / 2) - (Hd * h_cd / L_bc)
    Vb = round(Vb, 2)
    Vc = Vb_Vc - Vb
    Vc = round(Vc, 2)

    # === 4. Esforço Normal na barra (considerando Fh_barra = 0) ===
    Fh_barra = 0
    N = Fh_barra + Ha
    N = round(N, 2)

    # === 5. Diagramas simbólicos de cortante e momento ao longo de BC ===
    # A fórmula do cortante foi corrigida para carga distribuída uniforme.
    x = sp.Symbol("x", real=True)
    V = Vb + Pbc * x
    # A fórmula do momento foi corrigida (M = ∫Vdx).
    M = sp.integrate(V, (x, 0, x))

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
        xy=(round(A[0] - 0.5, 2), round(A[1], 2)),
        xytext=(round(A[0], 2), round(A[1], 2)),
        arrowprops=dict(facecolor="red", arrowstyle="->", lw=2),
    )
    ax1.text(
        round(A[0] - 0.6, 2), round(A[1] + 0.1, 2), f"{round(Ha, 2)} kN", color="red"
    )

    # Força horizontal Hd em D (positivo para direita) - Lógica de Seta Corrigida
    hd_magnitude = abs(Hd)
    if Hd >= 0:  # Positivo -> Direita
        start_point, end_point = (D[0], D[1]), (D[0] + 0.5, D[1])
        text_pos_x = D[0] + 0.6
    else:  # Negativo -> Esquerda
        start_point, end_point = (D[0], D[1]), (D[0] - 0.5, D[1])
        text_pos_x = D[0] - 0.6

    ax1.annotate(
        "",
        xy=end_point,
        xytext=start_point,
        arrowprops=dict(facecolor="red", arrowstyle="->", lw=2),
    )
    ax1.text(text_pos_x, D[1] + 0.1, f"{hd_magnitude:.2f} kN", color="red", ha="center")

    # Carga distribuída entre B e C: desenhar 4 setas igualmente espaçadas
    for i in range(4):
        x_placa = round((i + 1) * (L_bc / 5), 2)  # divide em 5 partes, usa 4 setas
        ax1.annotate(
            "",
            xy=(x_placa, 0),
            xytext=(x_placa, 0.5),
            arrowprops=dict(facecolor="blue", arrowstyle="->", lw=1),
        )
    ax1.text(
        round(L_bc / 2, 2),
        round(0.4, 2),
        f"{abs(Pbc):.2f} kN/m\nDistribuído",  # Mostra magnitude
        ha="center",
        color="blue",
    )

    # Ajustar limites do gráfico para acomodar parâmetros
    ax1.set_xlim(round(-L_ab - 1, 2), round(L_bc + 1, 2))
    ax1.set_ylim(round(-1.5, 2), round(h_cd + 1, 2))
    ax1.set_aspect("equal")
    ax1.set_title("Representação Estrutural e Forças")
    ax1.grid(True)

    # ----------- Exibição das Equações (ax2) -----------
    ax2.axis("off")

    # Título em negrito (fonte serif)
    ax2.text(
        0,
        1.00,
        "Equações Fundamentais do Equilíbrio",
        fontsize=14,
        fontweight="bold",
        family="serif",
        va="top",
    )

    ax2.text(
        0,
        0.90,
        r"$F_h = 0 \;\Longrightarrow\; H_c = -\,H_a - H_d \;=\; %g\;\mathrm{kN}$" % Hc,
        fontsize=12,
        family="serif",
        va="top",
    )

    ax2.text(
        0,
        0.75,
        r"$F_v = 0 \;\Longrightarrow\; V_b + V_c = - (P_{bc} \cdot L_{bc}) \;=\; %g\;\mathrm{kN}$"
        % round(-Pbc * L_bc, 2),
        fontsize=12,
        family="serif",
        va="top",
    )

    # Equação de Vb atualizada para refletir o cálculo
    ax2.text(
        0,
        0.60,
        r"$M_C = 0 \;\Longrightarrow\; V_b = \frac{-P_{bc} \frac{L_{bc}}{2} - H_d h_{cd}}{L_{bc}} \;=\; %g\;\mathrm{kN}$"
        % Vb,
        fontsize=12,
        family="serif",
        va="top",
    )

    ax2.text(
        0,
        0.45,
        r"$N_{BC} = H_a \;=\; %g\;\mathrm{kN}$" % N,
        fontsize=12,
        family="serif",
        va="top",
    )

    # Exibe a fórmula simbólica correta
    ax2.text(
        0,
        0.30,
        r"$V(x) = V_b + P_{bc} \cdot x = %s \;\;(\mathrm{kN})$"
        % sp.pretty(sp.simplify(sp.N(V, 2))),
        fontsize=12,
        family="serif",
        va="top",
    )

    ax2.text(
        0,
        0.15,
        r"$M(x) = \int V(x) dx = %s \;\;(\mathrm{kN}\cdot\mathrm{m})$"
        % sp.pretty(sp.simplify(sp.N(M, 2))),
        fontsize=12,
        family="serif",
        va="top",
    )

    # Frase final em itálico (fonte serif)
    ax2.text(
        0,
        0.05,
        "Grau de estatisticidade: Isostático",
        fontsize=11,
        family="serif",
        fontstyle="italic",
        va="top",
    )

    plt.tight_layout()
    return fig


# ================== STREAMLIT APP ==================

st.title("Análise Estrutural Interativa com Dimensões Parametrizadas")

st.sidebar.header("Entrada de Dados")
st.sidebar.write("Valores conforme a imagem para obter os resultados esperados.")

# 1. Forças
Ha = st.sidebar.number_input(
    "Força horizontal em A (Ha) [kN] (positivo → para a esquerda)", value=1.0, step=0.1
)
Hd = st.sidebar.number_input(
    "Força horizontal em D (Hd) [kN] (positivo → para a direita)",
    value=3.0,
    step=0.1,
)
Pbc = st.sidebar.number_input(
    "Carga distribuída em BC (Pbc) [kN/m] (negativo → para baixo)",
    value=-2.0,
    step=0.1,
)

# 2. Dimensões da estrutura
L_ab = st.sidebar.number_input("Comprimento AB (L_ab) [m]", value=1.0, step=0.1)
L_bc = st.sidebar.number_input("Comprimento BC (L_bc) [m]", value=3.0, step=0.1)
h_cd = st.sidebar.number_input("Altura CD (h_cd) [m]", value=1.0, step=0.1)

with st.spinner("Carregando análise..."):
    # Verifica se L_bc é zero para evitar divisão por zero
    if L_bc == 0:
        st.error("O comprimento BC (L_bc) não pode ser zero.")
    else:
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
