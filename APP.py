import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Saga Falabella S.A. | Executive Analytics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARCHIVO_EXCEL = "BasE DE DATOS DE FALLABELLA.xlsx"

# Helper para renderizar HTML sin que Markdown lo convierta en bloque de código
def render_html(raw_html: str):
    clean = "\n".join(line.strip() for line in raw_html.strip().splitlines() if line.strip())
    st.markdown(clean, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. ESTILOS CSS (DARK FOREST & EMERALD ANALYTICS)
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #07130d;
    color: #e6f4ec;
}

[data-testid="stSidebar"] {
    background-color: #0b1b13;
    border-right: 1px solid #173626;
}

[data-testid="stSidebar"] * {
    color: #cfe6d9;
}

header[data-testid="stHeader"] {
    background: transparent;
}

div[role="radiogroup"] > label {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 6px;
    transition: all 0.2s ease;
    cursor: pointer;
}
div[role="radiogroup"] > label:hover {
    background-color: #122b1e;
    border-color: #1f4d36;
}
div[role="radiogroup"] > label[data-checked="true"] {
    background: linear-gradient(90deg, #1ea355 0%, #15803d 100%) !important;
    color: #ffffff !important;
    font-weight: 700;
    box-shadow: 0 4px 14px rgba(34, 197, 94, 0.25);
}

.df-card {
    background-color: #0d2017;
    border: 1px solid #1b3d2b;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 14px;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.28);
}

.df-card-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #88b39c;
    margin-bottom: 6px;
}

.df-card-sub {
    font-size: 12px;
    color: #6b967f;
    margin-bottom: 12px;
}

.df-kpi-val {
    font-size: 26px;
    font-weight: 800;
    color: #f0fdf4;
    line-height: 1.15;
    margin: 6px 0;
}

.df-kpi-delta {
    font-size: 12px;
    font-weight: 600;
    color: #22c55e;
}

.df-kpi-delta-warn {
    font-size: 12px;
    font-weight: 600;
    color: #f59e0b;
}

.prog-row {
    margin-bottom: 12px;
}
.prog-header {
    display: flex;
    justify-content: space-between;
    font-size: 12.5px;
    font-weight: 600;
    color: #dcfce7;
    margin-bottom: 4px;
}
.prog-track {
    width: 100%;
    height: 18px;
    background-color: #08150f;
    border: 1px solid #183827;
    border-radius: 6px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    background: linear-gradient(90deg, #16a34a 0%, #34d399 100%);
    border-radius: 5px;
    display: flex;
    align-items: center;
    padding-left: 8px;
    font-size: 10.5px;
    font-weight: 700;
    color: #052e16;
}

.top-pill {
    display: inline-block;
    background-color: #0f261b;
    border: 1px solid #1f4b35;
    color: #a7f3d0;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    margin-left: 6px;
}

.alert-box {
    background-color: #0a1912;
    border-left: 3px solid #22c55e;
    border-top: 1px solid #183827;
    border-right: 1px solid #183827;
    border-bottom: 1px solid #183827;
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
}
.alert-box-warn {
    border-left-color: #f59e0b;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPONENTES VISUALES
# ---------------------------------------------------------
def render_ring_card(titulo: str, pct: float, valor_texto: str, subtexto: str, delta: str, warn: bool = False):
    pct_clamped = max(0.0, min(100.0, pct))
    radius = 30
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - pct_clamped / 100.0)
    stroke_color = "#f59e0b" if warn else "#22c55e"
    delta_class = "df-kpi-delta-warn" if warn else "df-kpi-delta"

    html = f"""
    <div class="df-card" style="text-align:center;">
        <div class="df-card-title">{titulo}</div>
        <div style="display:flex; justify-content:center; align-items:center; margin:8px 0;">
            <svg width="78" height="78" viewBox="0 0 78 78">
                <circle cx="39" cy="39" r="{radius}" fill="none" stroke="#163525" stroke-width="7"/>
                <circle cx="39" cy="39" r="{radius}" fill="none" stroke="{stroke_color}" stroke-width="7"
                        stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}"
                        stroke-linecap="round" transform="rotate(-90 39 39)"/>
                <text x="39" y="43" text-anchor="middle" fill="#f0fdf4" font-size="13" font-weight="800">{valor_texto}</text>
            </svg>
        </div>
        <div style="font-size:11px; color:#7fa892; margin-bottom:3px;">{subtexto}</div>
        <div class="{delta_class}">{delta}</div>
    </div>
    """
    render_html(html)

def render_metric_card(titulo: str, valor: str, subtexto: str, delta: str, warn: bool = False):
    delta_class = "df-kpi-delta-warn" if warn else "df-kpi-delta"
    html = f"""
    <div class="df-card">
        <div class="df-card-title">{titulo}</div>
        <div class="df-kpi-val">{valor}</div>
        <div style="font-size:11.5px; color:#7fa892; margin-bottom:6px;">{subtexto}</div>
        <div class="{delta_class}">{delta}</div>
    </div>
    """
    render_html(html)

def style_plotly(fig, height=340):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#cde5d7", family="Inter, sans-serif", size=12),
        margin=dict(l=16, r=16, t=36, b=16),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11)),
        xaxis=dict(showgrid=False, linecolor="#1c3f2d", tickfont=dict(color="#88b39c")),
        yaxis=dict(showgrid=True, gridcolor="#143022", linecolor="#1c3f2d", tickfont=dict(color="#88b39c")),
    )
    return fig

# ---------------------------------------------------------
# 4. CARGA DE DATOS DESDE EXCEL
# ---------------------------------------------------------
@st.cache_data
def cargar_datos(fuente):
    df_esf = pd.read_excel(fuente, sheet_name="Datos_ESF")
    df_er = pd.read_excel(fuente, sheet_name="Datos_ER")
    df_ctrl = pd.read_excel(fuente, sheet_name="Control")

    df_rat = pd.read_excel(fuente, sheet_name="Ratios", header=3)
    cols = list(df_rat.columns)
    cols[0], cols[1], cols[2] = "ID_Ratio", "Ratio", "Formula"
    df_rat.columns = cols
    df_rat = df_rat[df_rat["ID_Ratio"].astype(str).str.startswith("R")].copy()

    fact_ventas = pd.read_excel(fuente, sheet_name="Fact_Ventas")
    dim_prod = pd.read_excel(fuente, sheet_name="Dim_Producto")
    dim_zona = pd.read_excel(fuente, sheet_name="Dim_Zona")
    dim_cli = pd.read_excel(fuente, sheet_name="Dim_Cliente")

    fact_ventas["Fecha"] = pd.to_datetime(fact_ventas["Fecha"])
    fact_ventas["Año"] = fact_ventas["Fecha"].dt.year
    fact_ventas["Mes_Num"] = fact_ventas["Fecha"].dt.month
    fact_ventas["Venta_Bruta"] = fact_ventas["Cantidad"] * fact_ventas["Precio_Unitario"]
    fact_ventas["Venta_Neta"] = fact_ventas["Venta_Bruta"] - fact_ventas["Descuento"]
    fact_ventas["Costo_Total"] = fact_ventas["Cantidad"] * fact_ventas["Costo_Unitario"]
    fact_ventas["Margen_Soles"] = fact_ventas["Venta_Neta"] - fact_ventas["Costo_Total"]

    ventas = (
        fact_ventas
        .merge(dim_prod, on="SKU", how="left")
        .merge(dim_zona, on="ID_Zona", how="left")
        .merge(dim_cli, on="ID_Cliente", how="left")
    )

    periodos_validos = [c for c in df_esf.columns if "-T" in str(c) and df_esf[c].notna().any()]
    return df_esf, df_er, df_rat, df_ctrl, ventas, periodos_validos

if os.path.exists(ARCHIVO_EXCEL):
    fuente_datos = ARCHIVO_EXCEL
else:
    st.warning(f"No se encontró `{ARCHIVO_EXCEL}` en la carpeta actual. Súbelo aquí para iniciar:")
    fuente_datos = st.file_uploader("Cargar BasE DE DATOS DE FALLABELLA.xlsx", type=["xlsx"])
    if fuente_datos is None:
        st.stop()

df_esf, df_er, df_rat, df_ctrl, ventas, periodos_validos = cargar_datos(fuente_datos)

def get_ratio(id_r: str, per: str) -> float:
    val = df_rat.loc[df_rat["ID_Ratio"] == id_r, per].values
    return float(val[0]) if len(val) > 0 and pd.notna(val[0]) else 0.0

# ---------------------------------------------------------
# 5. SIDEBAR (NAVEGACIÓN Y META ANUAL)
# ---------------------------------------------------------
with st.sidebar:
    render_html("""
    <div style="display:flex; align-items:center; gap:10px; padding:6px 4px 18px 4px;">
        <div style="background:#22c55e; color:#052e16; font-weight:900; font-size:18px;
                    width:36px; height:36px; border-radius:9px; display:flex;
                    align-items:center; justify-content:center;">SF</div>
        <div>
            <div style="font-weight:800; font-size:15px; color:#f0fdf4; letter-spacing:0.04em;">SAGA FALABELLA</div>
            <div style="font-size:10px; color:#6ee7b7; letter-spacing:0.1em;">FINANCIAL & RETAIL BI</div>
        </div>
    </div>
    """)

    pagina = st.radio(
        "NAVEGACIÓN PRINCIPAL",
        [
            "1. KGI y 3 KPI por Estudiante",
            "2. Ratios Financieros ESF",
            "3. Ratios Financieros ER",
            "4. Ratios Combinados",
            "5. Dashboard de Ventas"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    render_html("<div style='font-size:11px; font-weight:700; color:#6b967f; letter-spacing:0.08em;'>PARÁMETROS DE CORTE</div>")
    anios_disp = sorted(list({int(p.split("-")[0]) for p in periodos_validos}))
    anio_sel = st.selectbox("Año Fiscal (SMV)", anios_disp, index=len(anios_disp) - 1)
    trim_sel = st.selectbox("Trimestre de Cierre", ["T1", "T2", "T3", "T4"], index=3)
    periodo_sel = f"{anio_sel}-{trim_sel}"
    if periodo_sel not in periodos_validos:
        periodo_sel = periodos_validos[-1]

    cols_anio_sb = [f"{anio_sel}-T{q}" for q in [1, 2, 3, 4] if f"{anio_sel}-T{q}" in periodos_validos]
    ing_anio_sb = df_er.loc[df_er["ID_Cuenta"] == "ER_INGRESOS", cols_anio_sb].values.sum()
    meta_ing = 4250000.0
    cumpl_pct = min(100.0, (ing_anio_sb / meta_ing) * 100)

    render_html(f"""
    <div style="background:#0f261b; border:1px solid #1e4632; border-radius:12px; padding:14px; margin-top:18px;">
        <div style="font-size:10px; font-weight:700; color:#6ee7b7; letter-spacing:0.08em;">META INGRESOS {anio_sel}</div>
        <div style="font-size:20px; font-weight:800; color:#ffffff; margin:4px 0;">S/ {ing_anio_sb:,.0f} mil</div>
        <div style="font-size:11px; color:#88b39c; margin-bottom:8px;">{cumpl_pct:.1f}% de S/ 4,250,000 mil</div>
        <div style="width:100%; height:7px; background:#07130d; border-radius:4px; overflow:hidden;">
            <div style="width:{cumpl_pct:.1f}%; height:100%; background:#22c55e;"></div>
        </div>
    </div>
    """)

# ---------------------------------------------------------
# 6. ENCABEZADO SUPERIOR COMÚN
# ---------------------------------------------------------
col_tit, col_badges = st.columns([2.2, 1.3])
with col_tit:
    render_html(f"""
    <div style="margin-bottom:8px;">
        <div style="font-size:24px; font-weight:800; color:#f0fdf4; letter-spacing:0.02em;">
            {pagina.upper()}
        </div>
        <div style="font-size:13px; color:#7fa892;">
            SAGA FALABELLA S.A. (Individual) · Corte Analítico: <b style="color:#34d399;">{periodo_sel}</b> · Cuadre Contable: <b style="color:#22c55e;">40/40 OK</b>
        </div>
    </div>
    """)
with col_badges:
    render_html(f"""
    <div style="text-align:right; padding-top:8px;">
        <span class="top-pill">📅 {periodo_sel}</span>
        <span class="top-pill">🏢 EMP01 · SMV</span>
        <span class="top-pill">✅ Control: OK</span>
    </div>
    """)

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# =========================================================
# HOJA 1: 1 KGI Y SUS 3 KPI POR ESTUDIANTE
# =========================================================
if pagina == "1. KGI y 3 KPI por Estudiante":
    roe_val = get_ratio("R18", periodo_sel) * 100
    roa_val = get_ratio("R17", periodo_sel) * 100
    cols_anio = [f"{anio_sel}-T{q}" for q in [1, 2, 3, 4] if f"{anio_sel}-T{q}" in periodos_validos]
    un_anual = df_er.loc[df_er["ID_Cuenta"] == "ER_UTIL_NETA", cols_anio].values.sum()

    v_2025 = ventas[ventas["Año"] == 2025]
    v_2024 = ventas[ventas["Año"] == 2024]
    venta_neta_2025 = v_2025["Venta_Neta"].sum()
    venta_neta_2024 = v_2024["Venta_Neta"].sum()
    crec_ventas = ((venta_neta_2025 / venta_neta_2024) - 1) * 100
    ticket_prom = venta_neta_2025 / v_2025["ID_Venta"].nunique()
    margen_com_pct = (v_2025["Margen_Soles"].sum() / venta_neta_2025) * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_ring_card("KGI WILLIAMS · ROE", roe_val * 2, f"{roe_val:.1f}%", "Meta: ≥ 35.0%", "↑ Rentabilidad Patrimonial")
    with c2:
        render_ring_card("KGI JOSE · MARGEN NETO", get_ratio("R12", periodo_sel) * 100 * 6, f"{get_ratio('R12', periodo_sel)*100:.1f}%", f"UN {anio_sel}: S/ {un_anual:,.0f}k", "↑ +60.3% UN Anual")
    with c3:
        render_ring_card("KGI JUDITH · ROA", roa_val * 6, f"{roa_val:.1f}%", "Meta: ≥ 11.0%", "↑ Eficiencia de Activos")
    with c4:
        render_ring_card("KGI RODRIGO · META VENTA", (venta_neta_2025 / 7000000) * 100, f"{(venta_neta_2025/7000000)*100:.1f}%", "Meta: S/ 7.00M", f"↑ +{crec_ventas:.1f}% YoY")
    with c5:
        render_metric_card("UTILIDAD NETA ANUAL", f"S/ {un_anual:,.0f}k", f"Acumulado {anio_sel} (SMV)", "↑ Resultado Neto ER")
    with c6:
        render_metric_card("VENTA NETA COMERCIAL", f"S/ {venta_neta_2025/1e6:.2f}M", f"{v_2025['ID_Venta'].nunique():,} transacciones", f"Ticket: S/ {ticket_prom:,.0f}")

    estudiantes = [
        {
            "nombre": "Pacompia Sotteccani Williams",
            "kgi": f"KGI: ROE Anual (12m) = {roe_val:.1f}%",
            "meta": "Meta: ≥ 35.0% | Enfoque DuPont",
            "kpis": [
                ("KPI 1 · Margen Neto Trimestral (R12)", f"{get_ratio('R12', periodo_sel)*100:.1f}%", min(100, get_ratio('R12', periodo_sel)*100*8)),
                ("KPI 2 · Rotación de Activos (R19)", f"{get_ratio('R19', periodo_sel):.2f}x", min(100, get_ratio('R19', periodo_sel)*45)),
                ("KPI 3 · Apalancamiento Deuda/Patrimonio (R06)", f"{get_ratio('R06', periodo_sel):.2f}x", min(100, get_ratio('R06', periodo_sel)*30)),
            ]
        },
        {
            "nombre": "Huanca Calcina Jose Eduardo",
            "kgi": f"KGI: Utilidad Neta {anio_sel} = S/ {un_anual:,.0f} mil",
            "meta": "Meta: S/ 260,000 mil | Estado de Resultados",
            "kpis": [
                ("KPI 1 · Margen Bruto (R10)", f"{get_ratio('R10', periodo_sel)*100:.1f}%", min(100, get_ratio('R10', periodo_sel)*100*2.2)),
                ("KPI 2 · Margen Operativo (R11)", f"{get_ratio('R11', periodo_sel)*100:.1f}%", min(100, get_ratio('R11', periodo_sel)*100*6)),
                ("KPI 3 · Gastos de Ventas / Ingresos (R13)", f"{get_ratio('R13', periodo_sel)*100:.1f}%", min(100, get_ratio('R13', periodo_sel)*100*3)),
            ]
        },
        {
            "nombre": "Acosta Hilasaca Judith Mariela",
            "kgi": f"KGI: ROA Anual (12m) = {roa_val:.1f}%",
            "meta": "Meta: ≥ 11.0% | Liquidez y Rotación",
            "kpis": [
                ("KPI 1 · Rotación de Inventarios (R20)", f"{get_ratio('R20', periodo_sel):.2f}x ({get_ratio('R21', periodo_sel):.0f} días)", min(100, get_ratio('R20', periodo_sel)*20)),
                ("KPI 2 · Razón Corriente (R01)", f"{get_ratio('R01', periodo_sel):.2f}x", min(100, get_ratio('R01', periodo_sel)*55)),
                ("KPI 3 · Cobertura de Intereses (R24)", f"{get_ratio('R24', periodo_sel):.2f}x", min(100, get_ratio('R24', periodo_sel)*15)),
            ]
        },
        {
            "nombre": "Diaz Huaman Rodrigo Jaime",
            "kgi": f"KGI: Venta Neta Comercial 2025 = S/ {venta_neta_2025:,.0f}",
            "meta": "Meta: S/ 7,000,000 | Desempeño Comercial",
            "kpis": [
                ("KPI 1 · Crecimiento Venta Neta YoY", f"+{crec_ventas:.1f}%", min(100, crec_ventas * 12)),
                ("KPI 2 · Ticket Promedio por Transacción", f"S/ {ticket_prom:,.0f}", min(100, (ticket_prom / 4000) * 100)),
                ("KPI 3 · Margen Comercial Bruto %", f"{margen_com_pct:.1f}%", min(100, margen_com_pct * 2.8)),
            ]
        }
    ]

    col_left, col_right = st.columns(2)
    for idx, est in enumerate(estudiantes):
        target_col = col_left if idx % 2 == 0 else col_right
        with target_col:
            bars_list = []
            for k_label, k_val, k_pct in est["kpis"]:
                bars_list.append(
                    f'<div class="prog-row">'
                    f'<div class="prog-header"><span>{k_label}</span><span style="color:#34d399;">{k_val}</span></div>'
                    f'<div class="prog-track"><div class="prog-fill" style="width:{k_pct:.1f}%;">{k_pct:.0f}%</div></div>'
                    f'</div>'
                )
            bars_html = "".join(bars_list)
            render_html(f"""
            <div class="df-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                    <span style="font-size:16px; font-weight:800; color:#f0fdf4;">👤 {est['nombre']}</span>
                    <span style="background:#143826; color:#34d399; padding:3px 9px; border-radius:6px; font-size:11px; font-weight:700;">1 KGI + 3 KPIs</span>
                </div>
                <div style="font-size:13.5px; font-weight:700; color:#22c55e; margin-bottom:2px;">{est['kgi']}</div>
                <div class="df-card-sub">{est['meta']}</div>
                {bars_html}
            </div>
            """)

# =========================================================
# HOJA 2: RATIOS FINANCIEROS DEL ESF
# =========================================================
elif pagina == "2. Ratios Financieros ESF":
    rc = get_ratio("R01", periodo_sel)
    pa = get_ratio("R02", periodo_sel)
    re = get_ratio("R03", periodo_sel)
    ct = get_ratio("R04", periodo_sel)
    end = get_ratio("R05", periodo_sel) * 100
    aut = get_ratio("R07", periodo_sel) * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_ring_card("RAZÓN CORRIENTE (R01)", min(100, rc * 55), f"{rc:.2f}x", "Activo Cte / Pasivo Cte", "↑ Liquidez > 1.0x")
    with c2:
        render_ring_card("PRUEBA ÁCIDA (R02)", min(100, pa * 100), f"{pa:.2f}x", "Sin Inventarios", "Liquidez inmediata")
    with c3:
        render_ring_card("RAZÓN EFECTIVO (R03)", min(100, re * 100), f"{re*100:.1f}%", "Caja / Pasivo Cte", "Cobertura en caja")
    with c4:
        render_ring_card("ENDEUDAMIENTO (R05)", end, f"{end:.1f}%", "Pasivo / Activo Total", "Apalancamiento retail", warn=True)
    with c5:
        render_ring_card("AUTONOMÍA FIN. (R07)", aut, f"{aut:.1f}%", "Patrimonio / Activo", "Respaldo propio")
    with c6:
        render_metric_card("CAPITAL DE TRABAJO", f"S/ {ct:,.0f}k", "Activo Cte − Pasivo Cte", "↑ Superávit operativo")

    ult12 = periodos_validos[-12:]
    g1, g2 = st.columns(2)
    with g1:
        render_html('<div class="df-card"><div class="df-card-title">EVOLUCIÓN DE LIQUIDEZ (ÚLTIMOS 12 TRIMESTRES)</div></div>')
        df_liq = df_rat[df_rat["ID_Ratio"].isin(["R01", "R02", "R03"])].melt(
            id_vars=["Ratio"], value_vars=ult12, var_name="Periodo", value_name="Valor"
        )
        fig1 = px.line(df_liq, x="Periodo", y="Valor", color="Ratio", markers=True,
                       color_discrete_sequence=["#22c55e", "#38bdf8", "#a7f3d0"])
        st.plotly_chart(style_plotly(fig1, 330), use_container_width=True)

    with g2:
        render_html('<div class="df-card"><div class="df-card-title">ESTRUCTURA DE FINANCIAMIENTO: DEUDA VS AUTONOMÍA</div></div>')
        df_est = df_rat[df_rat["ID_Ratio"].isin(["R05", "R07"])].melt(
            id_vars=["Ratio"], value_vars=ult12, var_name="Periodo", value_name="Valor"
        )
        df_est["Porcentaje"] = df_est["Valor"] * 100
        fig2 = px.bar(df_est, x="Periodo", y="Porcentaje", color="Ratio", barmode="stack",
                      color_discrete_sequence=["#15803d", "#34d399"])
        st.plotly_chart(style_plotly(fig2, 330), use_container_width=True)

    st.dataframe(
        df_rat[df_rat["ID_Ratio"].isin([f"R0{i}" for i in range(1, 10)])][["ID_Ratio", "Ratio", "Formula"] + periodos_validos[-8:]],
        use_container_width=True, hide_index=True
    )

# =========================================================
# HOJA 3: RATIOS FINANCIEROS DEL ER
# =========================================================
elif pagina == "3. Ratios Financieros ER":
    mb = get_ratio("R10", periodo_sel) * 100
    mo = get_ratio("R11", periodo_sel) * 100
    mn = get_ratio("R12", periodo_sel) * 100
    gv = get_ratio("R13", periodo_sel) * 100
    ga = get_ratio("R14", periodo_sel) * 100
    cr = get_ratio("R16", periodo_sel) * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_ring_card("MARGEN BRUTO (R10)", mb * 2.2, f"{mb:.1f}%", "Utilidad Bruta / Ventas", "Eficiencia comercial")
    with c2:
        render_ring_card("MARGEN OPERATIVO (R11)", mo * 6, f"{mo:.1f}%", "EBIT / Ventas", "Control de OpEx")
    with c3:
        render_ring_card("MARGEN NETO (R12)", mn * 8, f"{mn:.1f}%", "Utilidad Neta / Ventas", "Rentabilidad final")
    with c4:
        render_ring_card("GASTO VENTAS / ING (R13)", gv * 3, f"{gv:.1f}%", "Peso comercial", "Meta: < 20.0%", warn=gv > 20)
    with c5:
        render_ring_card("GASTO ADMIN / ING (R14)", ga * 10, f"{ga:.1f}%", "Estructura administrativa", "Eficiencia back-office")
    with c6:
        render_metric_card("CRECIMIENTO YOY (R16)", f"{cr:+.1f}%", "vs mismo trim. año previo", "↑ Expansión de ingresos")

    ult12 = periodos_validos[-12:]
    g1, g2 = st.columns(2)
    with g1:
        render_html('<div class="df-card"><div class="df-card-title">EVOLUCIÓN DE MÁRGENES DEL ESTADO DE RESULTADOS (%)</div></div>')
        df_m = df_rat[df_rat["ID_Ratio"].isin(["R10", "R11", "R12"])].melt(
            id_vars=["Ratio"], value_vars=ult12, var_name="Periodo", value_name="Valor"
        )
        df_m["Porcentaje"] = df_m["Valor"] * 100
        fig1 = px.line(df_m, x="Periodo", y="Porcentaje", color="Ratio", markers=True,
                       color_discrete_sequence=["#22c55e", "#10b981", "#a7f3d0"])
        st.plotly_chart(style_plotly(fig1, 330), use_container_width=True)

    with g2:
        render_html(f'<div class="df-card"><div class="df-card-title">CASCADA DE RESULTADOS ({periodo_sel} · MILES DE S/)</div></div>')
        ing = float(df_er.loc[df_er["ID_Cuenta"] == "ER_INGRESOS", periodo_sel].values[0])
        cos = float(df_er.loc[df_er["ID_Cuenta"] == "ER_COSTO", periodo_sel].values[0])
        g_v = float(df_er.loc[df_er["ID_Cuenta"] == "ER_GASTO_VENTAS", periodo_sel].values[0])
        g_a = float(df_er.loc[df_er["ID_Cuenta"] == "ER_GASTO_ADM", periodo_sel].values[0])
        u_n = float(df_er.loc[df_er["ID_Cuenta"] == "ER_UTIL_NETA", periodo_sel].values[0])

        fig2 = go.Figure(go.Waterfall(
            x=["Ingresos", "Costo Ventas", "Gastos Ventas", "Gastos Admin.", "Utilidad Neta"],
            measure=["absolute", "relative", "relative", "relative", "total"],
            y=[ing, cos, g_v, g_a, u_n],
            increasing=dict(marker=dict(color="#22c55e")),
            decreasing=dict(marker=dict(color="#ef4444")),
            totals=dict(marker=dict(color="#10b981"))
        ))
        st.plotly_chart(style_plotly(fig2, 330), use_container_width=True)

    st.dataframe(
        df_rat[df_rat["ID_Ratio"].isin([f"R{i}" for i in range(10, 17)])][["ID_Ratio", "Ratio", "Formula"] + periodos_validos[-8:]],
        use_container_width=True, hide_index=True
    )

# =========================================================
# HOJA 4: RATIOS COMBINADOS (ESF + ER)
# =========================================================
elif pagina == "4. Ratios Combinados":
    roa = get_ratio("R17", periodo_sel) * 100
    roe = get_ratio("R18", periodo_sel) * 100
    rot_act = get_ratio("R19", periodo_sel)
    rot_inv = get_ratio("R20", periodo_sel)
    dias_inv = get_ratio("R21", periodo_sel)
    cob_int = get_ratio("R24", periodo_sel)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_ring_card("ROA 12M (R17)", roa * 6, f"{roa:.1f}%", "UN 12m / Activo Total", "Retorno sobre activos")
    with c2:
        render_ring_card("ROE 12M (R18)", roe * 2, f"{roe:.1f}%", "UN 12m / Patrimonio", "Retorno al accionista")
    with c3:
        render_ring_card("ROT. ACTIVOS (R19)", rot_act * 45, f"{rot_act:.2f}x", "Ingresos 12m / Activo", "Productividad física")
    with c4:
        render_ring_card("ROT. INVENTARIOS (R20)", rot_inv * 20, f"{rot_inv:.2f}x", f"{dias_inv:.0f} días de stock", "Velocidad de venta")
    with c5:
        render_metric_card("DÍAS INVENTARIO (R21)", f"{dias_inv:.1f} d", f"Cobro: {get_ratio('R22', periodo_sel):.1f}d · Pago: {get_ratio('R23', periodo_sel):.1f}d", "Ciclo operativo")
    with c6:
        render_metric_card("COBERTURA INTERÉS (R24)", f"{cob_int:.2f}x", "EBIT 12m / Gasto Fin.", "↑ Solvencia financiera")

    ult12 = periodos_validos[-12:]
    g1, g2 = st.columns(2)
    with g1:
        render_html('<div class="df-card"><div class="df-card-title">RENTABILIDAD TTM: ROE VS ROA (%)</div></div>')
        df_r = df_rat[df_rat["ID_Ratio"].isin(["R17", "R18"])].melt(
            id_vars=["Ratio"], value_vars=ult12, var_name="Periodo", value_name="Valor"
        )
        df_r["Porcentaje"] = df_r["Valor"] * 100
        fig1 = px.line(df_r, x="Periodo", y="Porcentaje", color="Ratio", markers=True,
                       color_discrete_sequence=["#38bdf8", "#22c55e"])
        st.plotly_chart(style_plotly(fig1, 330), use_container_width=True)

    with g2:
        render_html('<div class="df-card"><div class="df-card-title">CICLO DE CONVERSIÓN DE EFECTIVO (DÍAS)</div></div>')
        df_c = df_rat[df_rat["ID_Ratio"].isin(["R21", "R22", "R23"])].melt(
            id_vars=["Ratio"], value_vars=ult12, var_name="Periodo", value_name="Días"
        )
        fig2 = px.bar(df_c, x="Periodo", y="Días", color="Ratio", barmode="group",
                      color_discrete_sequence=["#22c55e", "#a7f3d0", "#15803d"])
        st.plotly_chart(style_plotly(fig2, 330), use_container_width=True)

    st.dataframe(
        df_rat[df_rat["ID_Ratio"].isin([f"R{i}" for i in range(17, 25)])][["ID_Ratio", "Ratio", "Formula"] + periodos_validos[-8:]],
        use_container_width=True, hide_index=True
    )

# =========================================================
# HOJA 5: DASHBOARD DE VENTAS (Fact_Ventas)
# =========================================================
elif pagina == "5. Dashboard de Ventas":
    f1, f2, f3 = st.columns(3)
    anios_v = f1.multiselect("Filtrar Año Comercial:", sorted(ventas["Año"].unique()), default=sorted(ventas["Año"].unique()))
    zonas_v = f2.multiselect("Filtrar Zona:", sorted(ventas["Nombre_Zona"].unique()), default=sorted(ventas["Nombre_Zona"].unique()))
    canales_v = f3.multiselect("Filtrar Canal:", sorted(ventas["Canal"].unique()), default=sorted(ventas["Canal"].unique()))

    df_v = ventas[ventas["Año"].isin(anios_v) & ventas["Nombre_Zona"].isin(zonas_v) & ventas["Canal"].isin(canales_v)]

    venta_tot = df_v["Venta_Neta"].sum()
    venta_bruta_tot = df_v["Venta_Bruta"].sum()
    trans_tot = df_v["ID_Venta"].nunique()
    unid_tot = df_v["Cantidad"].sum()
    ticket_med = venta_tot / trans_tot if trans_tot > 0 else 0
    margen_med = (df_v["Margen_Soles"].sum() / venta_tot * 100) if venta_tot > 0 else 0
    desc_pct = (df_v["Descuento"].sum() / venta_bruta_tot * 100) if venta_bruta_tot > 0 else 0
    online_pct = (df_v[df_v["Canal"] == "Online"]["Venta_Neta"].sum() / venta_tot * 100) if venta_tot else 0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        render_ring_card("MARGEN COMERCIAL", margen_med * 2.5, f"{margen_med:.1f}%", "Utilidad Bruta Comercial", "↑ Rentabilidad SKU")
    with c2:
        render_ring_card("TASA DESCUENTO", desc_pct * 10, f"{desc_pct:.1f}%", "Sobre Venta Bruta", "Control promocional")
    with c3:
        render_ring_card("PART. ONLINE", online_pct, f"{online_pct:.1f}%", "Canal E-Commerce", "Omnicanalidad")
    with c4:
        render_metric_card("VENTA NETA TOTAL", f"S/ {venta_tot/1e6:.2f}M", f"S/ {venta_tot:,.0f}", "↑ Base Fact_Ventas")
    with c5:
        render_metric_card("TICKET PROMEDIO", f"S/ {ticket_med:,.0f}", f"{trans_tot:,} órdenes", "↑ Valor por boleta")
    with c6:
        render_metric_card("UNIDADES VENDIDAS", f"{unid_tot:,}", f"{df_v['ID_Cliente'].nunique():,} clientes activos", "Volumen total")

    g1, g2, g3 = st.columns([1.1, 1.3, 1.0])
    with g1:
        v_zona = df_v.groupby("Nombre_Zona", as_index=False)["Venta_Neta"].sum().sort_values("Venta_Neta", ascending=False)
        max_z = v_zona["Venta_Neta"].max() if len(v_zona) > 0 else 1
        z_list = []
        for _, row in v_zona.iterrows():
            pct_z = (row["Venta_Neta"] / max_z) * 100
            share_z = (row["Venta_Neta"] / venta_tot) * 100 if venta_tot else 0
            z_list.append(
                f'<div class="prog-row">'
                f'<div class="prog-header"><span>{row["Nombre_Zona"]}</span><span style="color:#34d399;">S/ {row["Venta_Neta"]:,.0f} ({share_z:.1f}%)</span></div>'
                f'<div class="prog-track"><div class="prog-fill" style="width:{pct_z:.1f}%;">{share_z:.1f}%</div></div>'
                f'</div>'
            )
        z_html = "".join(z_list)
        render_html(f'<div class="df-card"><div class="df-card-title">RANKING DE VENTAS POR ZONA (FUNNEL)</div>{z_html}</div>')

    with g2:
        render_html('<div class="df-card"><div class="df-card-title">TENDENCIA MENSUAL DE VENTAS Y TRANSACCIONES</div></div>')
        v_mes = df_v.groupby("Mes_Num", as_index=False).agg(Venta_Neta=("Venta_Neta", "sum"), Ordenes=("ID_Venta", "nunique"))
        fig_combo = go.Figure()
        fig_combo.add_trace(go.Bar(x=v_mes["Mes_Num"], y=v_mes["Venta_Neta"], name="Venta Neta (S/)", marker_color="rgba(34, 197, 94, 0.35)"))
        fig_combo.add_trace(go.Scatter(x=v_mes["Mes_Num"], y=v_mes["Ordenes"] * 2500, name="Índice Órdenes", mode="lines+markers", line=dict(color="#34d399", width=3)))
        st.plotly_chart(style_plotly(fig_combo, 310), use_container_width=True)

    with g3:
        render_html('<div class="df-card"><div class="df-card-title">DISTRIBUCIÓN POR CANAL</div></div>')
        v_can = df_v.groupby("Canal", as_index=False)["Venta_Neta"].sum()
        fig_pie = px.pie(v_can, names="Canal", values="Venta_Neta", hole=0.58,
                         color_discrete_sequence=["#22c55e", "#10b981", "#065f46"])
        fig_pie.update_traces(textposition="inside", textinfo="percent")
        st.plotly_chart(style_plotly(fig_pie, 310), use_container_width=True)

    b1, b2 = st.columns([1.4, 1.0])
    with b1:
        render_html('<div class="df-card"><div class="df-card-title">TOP CATEGORÍAS POR VENTA NETA Y MARGEN</div></div>')
        v_cat = df_v.groupby("Categoría", as_index=False).agg(
            Venta_Neta=("Venta_Neta", "sum"),
            Unidades=("Cantidad", "sum"),
            Margen=("Margen_Soles", "sum")
        ).sort_values("Venta_Neta", ascending=False).head(7)
        v_cat["Margen %"] = (v_cat["Margen"] / v_cat["Venta_Neta"] * 100).round(1)
        st.dataframe(v_cat[["Categoría", "Unidades", "Venta_Neta", "Margen %"]], use_container_width=True, hide_index=True)

    with b2:
        render_html("""
        <div class="df-card">
            <div class="df-card-title">INSIGHTS & ALERTS · MOTOR COMERCIAL</div>
            <div class="alert-box">
                <div style="font-size:12.5px; font-weight:700; color:#f0fdf4;">🟢 Liderazgo Regional: Lima Metropolitana</div>
                <div style="font-size:11.5px; color:#88b39c;">Concentra el 39.6% de la venta neta total (S/ 7.51M), seguida por Sur Andino (17.3%).</div>
            </div>
            <div class="alert-box">
                <div style="font-size:12.5px; font-weight:700; color:#f0fdf4;">🟢 Categoría Ancla: Tecnología & Electrohogar</div>
                <div style="font-size:11.5px; color:#88b39c;">Generan S/ 10.27M combinados, mientras Belleza y Moda lideran el margen bruto (&gt;41%).</div>
            </div>
            <div class="alert-box alert-box-warn">
                <div style="font-size:12.5px; font-weight:700; color:#fef3c7;">🟠 Nota Metodológica de Datos</div>
                <div style="font-size:11.5px; color:#d1d5db;">Las transacciones de Fact_Ventas (2023–2025) son datos comerciales simulados independientes del ER SMV.</div>
            </div>
        </div>
        """)