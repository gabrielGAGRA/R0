import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sympy as sp
import io


def resolver_estrutura(Ha, Hd, Pbc, L_bc, h_cd):
    # Equilíbrio horizontal: Hc = -Ha - Hd
    Hc = -Ha - Hd

    # Equilíbrio vertical: Vb + Vc = Pbc * L_bc
    Vbc = Pbc * L_bc
    Vb_Vc = Vbc
    # Momento em C: Vb = (Pbc * L_bc^2 / 2 - Hd * h_cd) / L_bc
    Vb = (Pbc * L_bc**2 / 2 - Hd * h_cd) / L_bc
    Vb = round(Vb, 2)

    Vc = Vb_Vc - Vb
    Vc = round(Vc, 2)

    # Força normal na barra BC: N = -Ha
    Fh_barra = 0
    N = Fh_barra - Ha
    N = round(N, 2)

    x = sp.Symbol("x", real=True)
    # Função cortante: V(x) = Vb - Pbc * x
    V = Vb - Pbc * x

    # Função momento fletor: M(x) = ∫V(x)dx
    M = sp.integrate(V, (x, 0, x))
    M_expanded = sp.expand(M)

    Hc = round(Hc, 2)

    return Hc, Vb, Vc, N, sp.simplify(V), sp.simplify(M), sp.simplify(M_expanded)


def plot_estrutura_e_equacoes(Ha, Hd, Pbc, L_ab, L_bc, h_cd):
    Hc, Vb, Vc, N, V, M, M_expanded = resolver_estrutura(Ha, Hd, Pbc, L_bc, h_cd)

    A = (-L_ab, 0)
    B = (0, 0)
    C = (L_bc, 0)
    D = (L_bc, h_cd)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 9), gridspec_kw={"height_ratios": [2, 1]}
    )

    ax1.plot([A[0], B[0]], [A[1], B[1]], "k-", linewidth=2.5)
    ax1.plot([B[0], C[0]], [B[1], C[1]], "k-", linewidth=2.5)
    ax1.plot([C[0], D[0]], [C[1], D[1]], "k-", linewidth=2.5)

    support_height = 0.08 * max(L_bc, h_cd, 2)
    support_base_width = support_height * 1.5

    tri_c_verts = [
        [C[0], C[1]],
        [C[0] - support_base_width / 2, C[1] - support_height],
        [C[0] + support_base_width / 2, C[1] - support_height],
    ]
    ax1.add_patch(
        patches.Polygon(
            tri_c_verts,
            closed=True,
            facecolor="#90ee90",
            edgecolor="darkgreen",
            linewidth=1.5,
        )
    )
    ground_y_c = C[1] - support_height
    ground_x_start_c = C[0] - support_base_width * 0.7
    ground_x_end_c = C[0] + support_base_width * 0.7
    ax1.plot(
        [ground_x_start_c, ground_x_end_c],
        [ground_y_c, ground_y_c],
        "k-",
        linewidth=1.5,
    )
    for i in range(8):
        hatch_x = ground_x_start_c + i * (ground_x_end_c - ground_x_start_c) / 7
        ax1.plot(
            [hatch_x, hatch_x - support_height * 0.25],
            [ground_y_c, ground_y_c - support_height * 0.25],
            "k-",
            linewidth=1,
        )

    tri_b_verts = [
        [B[0], B[1]],
        [B[0] - support_base_width / 2, B[1] - support_height],
        [B[0] + support_base_width / 2, B[1] - support_height],
    ]
    ax1.add_patch(
        patches.Polygon(
            tri_b_verts,
            closed=True,
            facecolor="#add8e6",
            edgecolor="darkblue",
            linewidth=1.5,
        )
    )
    roller_radius = support_height * 0.15
    roller_y = B[1] - support_height - roller_radius
    ax1.add_patch(
        patches.Circle(
            (B[0] - support_base_width * 0.25, roller_y),
            roller_radius,
            fill=True,
            color="darkblue",
        )
    )
    ax1.add_patch(
        patches.Circle(
            (B[0] + support_base_width * 0.25, roller_y),
            roller_radius,
            fill=True,
            color="darkblue",
        )
    )
    ground_line_y_b = roller_y - roller_radius
    ax1.plot(
        [B[0] - support_base_width * 0.7, B[0] + support_base_width * 0.7],
        [ground_line_y_b, ground_line_y_b],
        "k-",
        linewidth=1.5,
    )

    for point, label, dx, dy in zip(
        [A, B, C, D],
        ["A", "B\n(Apoio Simples)", "     C\n  (Apoio Articulado)", "D"],
        [-0.1 * L_ab, 0.0, 0.2 * L_bc, -0.1 * L_bc],
        [-0.2, 0.1, -0.1, 0.1],
    ):
        ax1.plot(point[0], point[1], "ko")
        ax1.text(point[0] + dx, point[1] + dy, label, fontsize=10, ha="center")

    arrow_props_h = dict(
        facecolor="red", arrowstyle="->,head_width=0.5,head_length=1.0", lw=2.5
    )

    ha_magnitude = abs(Ha)
    if Ha <= 0:
        start_point_ha, end_point_ha = (A[0], A[1]), (A[0] - 0.5, A[1])
        text_pos_ha_x = A[0] - 0.6
    else:
        start_point_ha, end_point_ha = (A[0], A[1]), (A[0] + 0.5, A[1])
        text_pos_ha_x = A[0] + 0.6

    ax1.annotate("", xy=end_point_ha, xytext=start_point_ha, arrowprops=arrow_props_h)
    ax1.text(
        text_pos_ha_x,
        A[1] + 0.1,
        f"{ha_magnitude:.2f} kN",
        color="red",
        fontweight="bold",
        ha="center",
    )

    hd_magnitude = abs(Hd)
    if Hd >= 0:
        start_point, end_point = (D[0], D[1]), (D[0] + 0.5, D[1])
        text_pos_x = D[0] + 0.6
    else:
        start_point, end_point = (D[0], D[1]), (D[0] - 0.5, D[1])
        text_pos_x = D[0] - 0.6
    ax1.annotate("", xy=end_point, xytext=start_point, arrowprops=arrow_props_h)
    ax1.text(
        text_pos_x,
        D[1] + 0.1,
        f"{hd_magnitude:.2f} kN",
        color="red",
        ha="center",
        fontweight="bold",
    )

    arrow_props_v = dict(
        facecolor="blue", arrowstyle="->,head_width=0.4,head_length=0.8", lw=1.5
    )
    for i in range(5):
        x_placa = (i + 1) * (L_bc / 6)
        ax1.annotate(
            "", xy=(x_placa, 0), xytext=(x_placa, 0.5), arrowprops=arrow_props_v
        )
    ax1.text(
        L_bc / 2,
        0.4,
        f"{abs(Pbc):.2f} kN/m\nDistribuído",
        ha="center",
        color="blue",
        fontweight="bold",
    )

    ax1.set_xlim(-L_ab - 1, L_bc + 1)
    ax1.set_ylim(-1.5 * support_height, h_cd + 1)
    ax1.set_aspect("equal")
    ax1.set_title("Representação Estrutural e Forças", fontsize=16, family="serif")
    ax1.grid(True)

    ax2.axis("off")
    eq_font_size = 12
    eq_font_family = "serif"

    ax2.text(
        0,
        1.0,
        "Equações Fundamentais do Equilíbrio",
        fontsize=16,
        fontweight="bold",
        family=eq_font_family,
        va="top",
    )
    ax2.text(
        0,
        0.9,
        r"$F_h = 0 \Longrightarrow H_c = -H_a - H_d = %g\,\mathrm{kN}$" % Hc,
        fontsize=eq_font_size,
        family=eq_font_family,
        va="top",
    )
    ax2.text(
        0,
        0.75,
        r"$F_v = 0 \Longrightarrow V_b + V_c = P_{bc} \cdot L_{bc} = %g\,\mathrm{kN}$"
        % round(Pbc * L_bc, 2),
        fontsize=eq_font_size,
        family=eq_font_family,
        va="top",
    )
    ax2.text(
        0,
        0.60,
        r"$M_C = 0 \Longrightarrow V_b = \frac{P_{bc} \frac{L^2_{bc}}{2} - H_d h_{cd}}{L_{bc}} = %g\,\mathrm{kN}$"
        % Vb,
        fontsize=eq_font_size,
        family=eq_font_family,
        va="top",
    )
    ax2.text(
        0,
        0.45,
        r"$N_{BC} = -H_a = %g\,\mathrm{kN}$" % N,
        fontsize=eq_font_size,
        family=eq_font_family,
        va="top",
    )
    ax2.text(
        0,
        0.30,
        r"$V(x) = V_b - P_{bc} \cdot x = %s\,(\mathrm{kN})$"
        % str(sp.simplify(sp.N(V, 2))),
        fontsize=eq_font_size,
        family=eq_font_family,
        va="top",
    )

    m_pretty = str(sp.simplify(sp.N(M, 2)))
    m_expanded_pretty = str(sp.simplify(sp.N(M_expanded, 2)))
    m_text = (
        f"{m_pretty} = {m_expanded_pretty}"
        if m_pretty != m_expanded_pretty
        else m_pretty
    )
    ax2.text(
        0,
        0.15,
        r"$M(x) = \int V(x) dx = %s\,(\mathrm{kN}\cdot\mathrm{m})$" % m_text,
        fontsize=eq_font_size,
        family=eq_font_family,
        va="top",
    )

    # Grau de estatisticidade: Isostático
    ax2.text(
        0,
        0.0,
        "Grau de estatisticidade: Isostático",
        fontsize=11,
        family=eq_font_family,
        fontstyle="italic",
        va="top",
    )

    plt.tight_layout(pad=2.0)
    return fig


st.title("Análise Estrutural Interativa com Dimensões Parametrizadas")

st.sidebar.header("Entrada de Dados")
st.sidebar.write("Use os valores da imagem de exemplo para replicar os resultados.")

Ha = st.sidebar.number_input(
    "Força horizontal em A (Ha) [kN] (positivo → para a direita)", value=-1.0, step=0.1
)
Hd = st.sidebar.number_input(
    "Força horizontal em D (Hd) [kN] (positivo → para a direita)", value=3.0, step=0.1
)
Pbc = st.sidebar.number_input(
    "Carga distribuída em BC (Pbc) [kN/m] (positivo → para baixo)", value=2.0, step=0.1
)

L_ab = st.sidebar.number_input(
    "Comprimento AB (L_ab) [m]", value=1.0, step=0.1, min_value=0.1
)
L_bc = st.sidebar.number_input(
    "Comprimento BC (L_bc) [m]", value=3.0, step=0.1, min_value=0.1
)
h_cd = st.sidebar.number_input(
    "Altura CD (h_cd) [m]", value=1.0, step=0.1, min_value=0.1
)

with st.spinner("Carregando análise..."):
    if L_bc == 0:
        st.error("O comprimento BC (L_bc) não pode ser zero.")
    else:
        fig = plot_estrutura_e_equacoes(Ha, Hd, Pbc, L_ab, L_bc, h_cd)
        st.pyplot(fig)

        pdf_bytes = io.BytesIO()
        fig.savefig(pdf_bytes, format="pdf")
        pdf_bytes.seek(0)

        st.download_button(
            label="Download do PDF",
            data=pdf_bytes,
            file_name="analise_estrutura_parametrizada.pdf",
            mime="application/pdf",
        )
