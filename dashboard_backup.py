import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import os
import sys
import traceback

# Set page config
st.set_page_config(
    page_title="Dashboard Realisasi Belanja",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "show_sidebar" not in st.session_state:
    st.session_state.show_sidebar = True

# Theme styling
st.markdown("""
    <style>
    body {
        background: linear-gradient(180deg, #f5f8ff 0%, #eef4fb 100%);
        color: #0f172a;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid rgba(15, 23, 42, 0.08);
    }
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff, #e7efff);
        border: 1px solid rgba(37, 99, 235, 0.15);
        border-radius: 18px;
        padding: 18px;
    }
    .stButton>button {
        background-color: #2563eb;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.7rem 1rem;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
    }
    .css-1v3fvcr, .css-1d391kg {
        background: transparent;
    }
    h1 {
        color: #0f172a;
    }
    h2, h3, h4, h5, h6 {
        color: #1e293b;
    }
    .stSidebar [data-testid="stMarkdownContainer"] {
        margin-bottom: 1rem;
    }
    .css-18e3th9 {
        padding-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data with robust error handling
@st.cache_data
def load_data():
    """Load CSV dengan fallback paths dan error handling lengkap."""
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'Belanja_Full_Baru.csv'),
        'Belanja_Full_Baru.csv',
        '/Users/djpb/Documents/Dashboard Realisasi/Belanja_Full_Baru.csv'
    ]
    
    df = None
    last_error = None
    
    for p in possible_paths:
        try:
            if os.path.exists(p):
                df = pd.read_csv(p, delimiter=';')
                st.success(f"✅ Data loaded successfully from: {p}")
                break
        except Exception as e:
            last_error = str(e)
            continue
    
    if df is None:
        error_text = f"""
❌ **CRITICAL ERROR: Data file not found!**

**Tried paths:**
"""
        for p in possible_paths:
            exists = "✓" if os.path.exists(p) else "✗"
            error_text += f"\n{exists} {p}"
        
        error_text += f"""

**Current directory:** {os.getcwd()}
**Files in directory:** {', '.join(os.listdir('.')[:10])}
**Last error:** {last_error}

**Solution:**
1. Ensure 'Belanja_Full_Baru.csv' exists in the repository root
2. Run: `git add Belanja_Full_Baru.csv && git commit -m "Add data" && git push`
3. Check Streamlit Cloud logs for more details
        """
        st.error(error_text)
        st.stop()
    
    try:
        # Bersihkan data - ganti notasi ilmiah dengan angka normal
        for col in ['PAGU_DIPA', 'REALISASI', 'BLOKIR']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Hapus baris dengan nilai NaN di kolom penting
        df = df.dropna(subset=['NMDEPT', 'NMLOKASI', 'TAHUN'])
        
        # Convert kolom string ke string dan hapus whitespace
        df['NMDEPT'] = df['NMDEPT'].astype(str).str.strip()
        df['NMLOKASI'] = df['NMLOKASI'].astype(str).str.strip()
        df['TAHUN'] = df['TAHUN'].astype(int)
        
        # Hitung persentase realisasi dan selisih
        df['PERSEN_REALISASI'] = (df['REALISASI'] / df['PAGU_DIPA'] * 100).round(2)
        df['SELISIH'] = df['REALISASI'] - df['PAGU_DIPA']
        df['OVER_BUDGET'] = df['SELISIH'] > 0
        
        return df
    except Exception as e:
        st.error(f"❌ Error processing data: {str(e)}\n\n{traceback.format_exc()}")
        st.stop()

# Load data safely
try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Critical error during initialization: {str(e)}\n\n{traceback.format_exc()}")
    st.stop()

# Title
st.title("Dashboard Realisasi Belanja Kementerian")
st.markdown("---")

try:
    # Sidebar filters
    st.sidebar.header("🔍 Filter Data")

# Prepare filter options
tahun_list = sorted(df['TAHUN'].dropna().unique())
dept_list = sorted(df['NMDEPT'].dropna().unique())
lokasi_list = sorted(df['NMLOKASI'].dropna().unique())

# Tahun filter with "Semua Tahun" option
col1, col2 = st.sidebar.columns(2)
with col1:
    semua_tahun = st.sidebar.checkbox("✓ Semua Tahun", value=True, key="semua_tahun")

if semua_tahun:
    tahun_selected = tahun_list
else:
    tahun_selected = st.sidebar.multiselect(
        "Pilih Tahun:",
        tahun_list,
        default=[]
    )

# Kementerian filter with "Semua Kementerian" option
col1, col2 = st.sidebar.columns(2)
with col1:
    semua_dept = st.sidebar.checkbox("✓ Semua Kementerian", value=True, key="semua_dept")

if semua_dept:
    dept_selected = dept_list
else:
    dept_selected = st.sidebar.multiselect(
        "Pilih Kementerian:",
        dept_list,
        default=[]
    )

# Lokasi filter with "Semua Lokasi" option
col1, col2 = st.sidebar.columns(2)
with col1:
    semua_lokasi = st.sidebar.checkbox("✓ Semua Lokasi", value=True, key="semua_lokasi")

if semua_lokasi:
    lokasi_selected = lokasi_list
else:
    lokasi_selected = st.sidebar.multiselect(
        "Pilih Lokasi/Wilayah:",
        lokasi_list,
        default=[]
    )

# Submit button
st.sidebar.markdown("---")
submit_button = st.sidebar.button("🔄 Terapkan Filter", width='stretch')

if submit_button:
    st.success("✅ Filter telah diterapkan!")

# Filter data berdasarkan selection
df_filtered = df[
    (df['TAHUN'].isin(tahun_selected)) & 
    (df['NMDEPT'].isin(dept_selected)) &
    (df['NMLOKASI'].isin(lokasi_selected))
].copy()

# Tabs untuk berbagai views
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1️⃣ Realisasi vs Pagu per Tahun",
    "2️⃣ Realisasi per Wilayah",
    "3️⃣ Early Warning",
    "4️⃣ Realisasi per Kementerian",
    "5️⃣ Kegiatan Terbanyak",
    "6️⃣ Budget Prediction"
])

# ==================== TAB 1: REALISASI VS PAGU PER TAHUN ====================
with tab1:
    st.header("Realisasi dibanding Pagu Seluruh Kementerian per Tahun")
    
    # Agregasi data per tahun
    df_tahun = df_filtered.groupby('TAHUN').agg({
        'PAGU_DIPA': 'sum',
        'REALISASI': 'sum',
        'BLOKIR': 'sum'
    }).reset_index()
    
    df_tahun['PERSEN_REALISASI'] = (df_tahun['REALISASI'] / df_tahun['PAGU_DIPA'] * 100).round(2)
    df_tahun['SELISIH'] = df_tahun['REALISASI'] - df_tahun['PAGU_DIPA']
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_pagu = df_tahun['PAGU_DIPA'].sum()
    total_realisasi = df_tahun['REALISASI'].sum()
    avg_persen = (total_realisasi / total_pagu * 100) if total_pagu > 0 else 0
    
    with col1:
        st.metric("Total Pagu", f"Rp {total_pagu/1e12:.2f}T")
    with col2:
        st.metric("Total Realisasi", f"Rp {total_realisasi/1e12:.2f}T")
    with col3:
        st.metric("Persen Realisasi", f"{avg_persen:.1f}%")
    with col4:
        st.metric("Selisih", f"Rp {(total_realisasi-total_pagu)/1e12:.2f}T")
    
    st.markdown("---")
    
    # Chart 1: Bar chart comparison
    fig1 = go.Figure(data=[
        go.Bar(name='Pagu', x=df_tahun['TAHUN'], y=df_tahun['PAGU_DIPA'], marker_color='#3498db'),
        go.Bar(name='Realisasi', x=df_tahun['TAHUN'], y=df_tahun['REALISASI'], marker_color='#2ecc71')
    ])
    fig1.update_layout(
        title="Pagu vs Realisasi per Tahun",
        xaxis_title="Tahun",
        yaxis_title="Nilai (Rupiah)",
        barmode='group',
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig1, width='stretch')
    
    # Chart 2: Persentase Realisasi
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_tahun['TAHUN'],
        y=df_tahun['PERSEN_REALISASI'],
        mode='lines+markers',
        name='% Realisasi',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10)
    ))
    fig2.add_hline(y=100, line_dash="dash", line_color="red", annotation_text="Target 100%")
    fig2.update_layout(
        title="Persentase Realisasi per Tahun",
        xaxis_title="Tahun",
        yaxis_title="Persentase (%)",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig2, width='stretch')
    
    # Tabel Detail
    st.subheader("Detail Realisasi per Tahun")
    df_tahun_display = df_tahun.copy()
    df_tahun_display['PAGU_DIPA'] = df_tahun_display['PAGU_DIPA'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_tahun_display['REALISASI'] = df_tahun_display['REALISASI'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_tahun_display['SELISIH'] = df_tahun_display['SELISIH'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_tahun_display['PERSEN_REALISASI'] = df_tahun_display['PERSEN_REALISASI'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(df_tahun_display, width='stretch', hide_index=True)


# ==================== TAB 2: REALISASI PER WILAYAH ====================
with tab2:
    st.header("Realisasi per Lokasi/Wilayah")
    
    # Agregasi per lokasi
    df_lokasi = df_filtered.groupby('NMLOKASI').agg({
        'PAGU_DIPA': 'sum',
        'REALISASI': 'sum',
    }).reset_index()
    
    df_lokasi['PERSEN_REALISASI'] = (df_lokasi['REALISASI'] / df_lokasi['PAGU_DIPA'] * 100).round(2)
    df_lokasi = df_lokasi.sort_values('REALISASI', ascending=False)
    
    # Metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Wilayah", len(df_lokasi))
    with col2:
        st.metric("Realisasi Total", f"Rp {df_lokasi['REALISASI'].sum()/1e12:.2f}T")
    
    st.markdown("---")
    
    # Map coordinates for wilayah lokasi
    lokasi_coords = {
        'DKI JAKARTA': (-6.200000, 106.816666),
        'JAWA BARAT': (-6.900000, 107.600000),
        'JAWA TENGAH': (-7.000000, 110.416664),
        'DI YOGYAKARTA': (-7.795580, 110.369490),
        'JAWA TIMUR': (-7.250000, 112.750000),
        'ACEH': (5.556000, 95.323800),
        'SUMATERA UTARA': (2.990000, 99.020000),
        'SUMATERA BARAT': (-0.949190, 100.354530),
        'RIAU': (0.507800, 101.447800),
        'JAMBI': (-1.617400, 103.609200),
        'SUMATERA SELATAN': (-3.003900, 104.746300),
        'LAMPUNG': (-5.435200, 105.261200),
        'KALIMANTAN BARAT': (0.020000, 109.340000),
        'KALIMANTAN TENGAH': (-1.784700, 113.334200),
        'KALIMANTAN SELATAN': (-3.348900, 114.594200),
        'KALIMANTAN TIMUR': (0.492000, 117.153300),
        'KALIMANTAN UTARA': (1.721100, 116.728700),
        'SULAWESI UTARA': (1.487600, 124.841200),
        'SULAWESI TENGAH': (-0.895500, 121.691100),
        'SULAWESI SELATAN': (-4.540000, 119.999500),
        'SULAWESI TENGGARA': (-4.071400, 122.296800),
        'SULAWESI BARAT': (-2.983300, 119.666700),
        'GORONTALO': (0.538600, 123.059600),
        'BALI': (-8.340500, 115.091900),
        'NUSA TENGGARA BARAT': (-8.621200, 116.214600),
        'NUSA TENGGARA TIMUR': (-9.655000, 121.143100),
        'BENGKULU': (-3.797500, 102.257600),
        'KEPULAUAN BANGKA BELITUNG': (-2.741600, 107.564500),
        'KEPULAUAN RIAU': (1.041400, 104.088500),
        'MALUKU': (-3.210000, 129.183300),
        'MALUKU UTARA': (0.803700, 127.423600),
        'PAPUA': (-4.269700, 138.080800),
        'PAPUA BARAT': (-2.529000, 133.167000),
        'PAPUA PEGUNUNGAN': (-4.800000, 137.500000),
        'PAPUA SELATAN': (-5.300000, 138.000000),
        'PAPUA TENGAH': (-4.000000, 136.000000),
        'PAPUA BARAT DAYA': (-5.300000, 131.700000),
        'BANTEN': (-6.120000, 106.149000),
    }
    
    df_lokasi_map = df_lokasi.copy()
    df_lokasi_map['coords'] = df_lokasi_map['NMLOKASI'].map(lokasi_coords)
    df_lokasi_map = df_lokasi_map[df_lokasi_map['coords'].notna()].copy()
    df_lokasi_map[['lat', 'lon']] = pd.DataFrame(df_lokasi_map['coords'].tolist(), index=df_lokasi_map.index)
    
    # Provide a map and top wilayah side-by-side
    col_map, col_table = st.columns([2, 1])
    with col_map:
        st.subheader("Peta Realisasi Wilayah")
        if len(df_lokasi_map) > 0:
            fig_map = px.scatter_mapbox(
                df_lokasi_map,
                lat='lat',
                lon='lon',
                size='REALISASI',
                color='PERSEN_REALISASI',
                hover_name='NMLOKASI',
                hover_data={
                    'PAGU_DIPA': ':,.0f',
                    'REALISASI': ':,.0f',
                    'PERSEN_REALISASI': ':.2f',
                    'lat': False,
                    'lon': False,
                },
                color_continuous_scale='RdYlGn',
                size_max=40,
                zoom=3,
                mapbox_style='open-street-map',
                title='Peta Realisasi dan Persentase Realisasi per Wilayah'
            )
            fig_map.update_layout(height=520, margin=dict(l=0, r=0, t=50, b=0))
            st.plotly_chart(fig_map, width='stretch')
        else:
            st.warning("Peta belum tersedia untuk beberapa wilayah karena koordinat tidak ditemukan.")
    
    with col_table:
        st.subheader("Top 5 Wilayah")
        df_lokasi_top5 = df_lokasi.sort_values('PERSEN_REALISASI', ascending=False).head(5).copy()
        df_lokasi_top5['REALISASI'] = df_lokasi_top5['REALISASI'].apply(lambda x: f"Rp {x/1e12:.2f}T")
        df_lokasi_top5['PAGU_DIPA'] = df_lokasi_top5['PAGU_DIPA'].apply(lambda x: f"Rp {x/1e12:.2f}T")
        df_lokasi_top5['PERSEN_REALISASI'] = df_lokasi_top5['PERSEN_REALISASI'].apply(lambda x: f"{x:.2f}%")
        st.table(df_lokasi_top5[['NMLOKASI', 'REALISASI', 'PAGU_DIPA', 'PERSEN_REALISASI']].rename(columns={
            'NMLOKASI': 'Wilayah',
            'PAGU_DIPA': 'Pagu',
            'REALISASI': 'Realisasi',
            'PERSEN_REALISASI': '% Realisasi'
        }))
    
    st.markdown("---")
    
    # Chart: Top 15 Wilayah
    df_lokasi_top = df_lokasi.head(15)
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        y=df_lokasi_top['NMLOKASI'],
        x=df_lokasi_top['PAGU_DIPA'],
        name='Pagu',
        marker_color='#3498db',
        orientation='h'
    ))
    fig3.add_trace(go.Bar(
        y=df_lokasi_top['NMLOKASI'],
        x=df_lokasi_top['REALISASI'],
        name='Realisasi',
        marker_color='#2ecc71',
        orientation='h'
    ))
    fig3.update_layout(
        title="Top 15 Wilayah - Pagu vs Realisasi",
        xaxis_title="Nilai (Rupiah)",
        yaxis_title="Wilayah",
        barmode='group',
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig3, width='stretch')
    
    # Tabel lengkap
    st.subheader("Detail Realisasi per Wilayah")
    df_lokasi_display = df_lokasi.copy()
    df_lokasi_display['PAGU_DIPA'] = df_lokasi_display['PAGU_DIPA'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_lokasi_display['REALISASI'] = df_lokasi_display['REALISASI'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_lokasi_display['PERSEN_REALISASI'] = df_lokasi_display['PERSEN_REALISASI'].apply(lambda x: f"{x:.2f}%")
    df_lokasi_display = df_lokasi_display.rename(columns={
        'NMLOKASI': 'Wilayah',
        'PAGU_DIPA': 'Pagu',
        'REALISASI': 'Realisasi',
        'PERSEN_REALISASI': '% Realisasi'
    })
    
    st.dataframe(df_lokasi_display, width='stretch', hide_index=True)


# ==================== TAB 3: EARLY WARNING ====================
with tab3:
    st.header("⚠️ Indikator Early Warning (Over Budget)")
    
    # Filter data yang over budget
    df_warning = df_filtered[df_filtered['OVER_BUDGET']].copy()
    df_warning = df_warning.sort_values('SELISIH', ascending=False)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Item Over Budget", len(df_warning))
    with col2:
        st.metric("Total Selisih Positif", f"Rp {df_warning['SELISIH'].sum()/1e9:.2f}M")
    with col3:
        persen_over = (len(df_warning) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
        st.metric("Persentase Over Budget", f"{persen_over:.2f}%")
    
    st.markdown("---")
    
    # Filter untuk kategori selisih
    selisih_min = st.slider(
        "Filter Minimum Selisih (Miliaran Rp):",
        min_value=0,
        max_value=int(df_warning['SELISIH'].max()/1e9),
        value=0,
        step=1
    )
    
    df_warning_filtered = df_warning[df_warning['SELISIH'] >= selisih_min * 1e9]
    
    # Chart: Top 20 Over Budget
    df_warning_top = df_warning_filtered.head(20)
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=df_warning_top['SELISIH']/1e9,
        y=df_warning_top['NMDEPT'] + ' - ' + df_warning_top['NMLOKASI'],
        name='Selisih Positif',
        marker_color='#e74c3c',
        orientation='h',
        text=(df_warning_top['SELISIH']/1e9).round(1),
        textposition='outside'
    ))
    fig4.update_layout(
        title="Top 20 Item dengan Over Budget Tertinggi",
        xaxis_title="Selisih Positif (Miliaran Rp)",
        yaxis_title="Kementerian - Wilayah",
        height=700,
        hovermode='x unified'
    )
    st.plotly_chart(fig4, width='stretch')
    
    # Tabel warning
    st.subheader("Detail Items Over Budget")
    if len(df_warning_filtered) > 0:
        df_warning_display = df_warning_filtered.copy()
        df_warning_display = df_warning_display[[
            'NMDEPT', 'NMLOKASI', 'NMGIAT', 'TAHUN', 'PAGU_DIPA', 'REALISASI', 'SELISIH', 'PERSEN_REALISASI'
        ]]
        df_warning_display['PAGU_DIPA'] = df_warning_display['PAGU_DIPA'].apply(lambda x: f"Rp {x/1e9:.2f}M")
        df_warning_display['REALISASI'] = df_warning_display['REALISASI'].apply(lambda x: f"Rp {x/1e9:.2f}M")
        df_warning_display['SELISIH'] = df_warning_display['SELISIH'].apply(lambda x: f"Rp {x/1e9:.2f}M")
        df_warning_display['PERSEN_REALISASI'] = df_warning_display['PERSEN_REALISASI'].apply(lambda x: f"{x:.2f}%")
        
        df_warning_display = df_warning_display.rename(columns={
            'NMDEPT': 'Kementerian',
            'NMLOKASI': 'Wilayah',
            'NMGIAT': 'Kegiatan',
            'TAHUN': 'Tahun',
            'PAGU_DIPA': 'Pagu',
            'REALISASI': 'Realisasi',
            'SELISIH': 'Over Budget',
            'PERSEN_REALISASI': '% Realisasi'
        })
        
        st.dataframe(df_warning_display, width='stretch', hide_index=True)
    else:
        st.info("✅ Tidak ada item yang over budget dengan kriteria tersebut.")


# ==================== TAB 4: REALISASI PER KEMENTERIAN ====================
with tab4:
    st.header("Realisasi per Kementerian")
    
    # Agregasi per kementerian
    df_dept = df_filtered.groupby('NMDEPT').agg({
        'PAGU_DIPA': 'sum',
        'REALISASI': 'sum',
    }).reset_index()
    
    # Hitung persentase dengan safe division
    df_dept['PERSEN_REALISASI'] = df_dept.apply(
        lambda row: (row['REALISASI'] / row['PAGU_DIPA'] * 100) if row['PAGU_DIPA'] > 0 else 0,
        axis=1
    ).round(2)
    df_dept['SELISIH'] = df_dept['REALISASI'] - df_dept['PAGU_DIPA']
    
    # Hapus baris dengan PAGU_DIPA = 0
    df_dept = df_dept[df_dept['PAGU_DIPA'] > 0]
    df_dept = df_dept.sort_values('REALISASI', ascending=False)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Kementerian", len(df_dept))
    with col2:
        st.metric("Realisasi Total", f"Rp {df_dept['REALISASI'].sum()/1e12:.2f}T")
    with col3:
        avg_persen_dept = (df_dept['REALISASI'].sum() / df_dept['PAGU_DIPA'].sum() * 100) if df_dept['PAGU_DIPA'].sum() > 0 else 0
        st.metric("Rata-rata % Realisasi", f"{avg_persen_dept:.1f}%")
    
    st.markdown("---")
    
    # Scatter plot: Pagu vs Realisasi
    # Filter out any remaining NaN values for the scatter plot
    df_dept_scatter = df_dept.dropna(subset=['PERSEN_REALISASI'])
    
    if len(df_dept_scatter) > 0:
        fig5 = px.scatter(
            df_dept_scatter,
            x='PAGU_DIPA',
            y='REALISASI',
            size='PERSEN_REALISASI',
            hover_name='NMDEPT',
            color='PERSEN_REALISASI',
            color_continuous_scale='RdYlGn',
            title="Hubungan Pagu vs Realisasi per Kementerian",
            labels={
                'PAGU_DIPA': 'Pagu (Rp)',
                'REALISASI': 'Realisasi (Rp)',
                'PERSEN_REALISASI': '% Realisasi'
            },
            height=500
        )
        
        # Tambah diagonal line (perfect realization)
        max_val = max(df_dept_scatter['PAGU_DIPA'].max(), df_dept_scatter['REALISASI'].max())
        fig5.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Perfect Realization',
            line=dict(dash='dash', color='gray'),
            hoverinfo='skip'
        ))
        
        st.plotly_chart(fig5, width='stretch')
    else:
        st.warning("Tidak ada data yang cukup untuk menampilkan scatter plot")
    
    # Bar chart: Top Kementerian
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top 10 Kementerian (by Realisasi)")
        df_dept_top = df_dept.head(10)
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(
            x=df_dept_top['REALISASI'],
            y=df_dept_top['NMDEPT'],
            name='Realisasi',
            marker_color='#2ecc71',
            orientation='h'
        ))
        fig6.update_layout(
            title="",
            xaxis_title="Realisasi (Rp)",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig6, width='stretch')
    
    with col2:
        st.subheader("Persentase Realisasi")
        df_dept_persen = df_dept.sort_values('PERSEN_REALISASI', ascending=False).head(10)
        fig7 = go.Figure()
        colors = ['#2ecc71' if x >= 100 else '#3498db' for x in df_dept_persen['PERSEN_REALISASI']]
        fig7.add_trace(go.Bar(
            x=df_dept_persen['PERSEN_REALISASI'],
            y=df_dept_persen['NMDEPT'],
            name='% Realisasi',
            marker_color=colors,
            orientation='h'
        ))
        fig7.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="Target 100%")
        fig7.update_layout(
            title="",
            xaxis_title="Persentase (%)",
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig7, width='stretch')
    
    # Tabel lengkap
    st.subheader("Detail Realisasi per Kementerian")
    df_dept_display = df_dept.copy()
    df_dept_display['PAGU_DIPA'] = df_dept_display['PAGU_DIPA'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_dept_display['REALISASI'] = df_dept_display['REALISASI'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_dept_display['SELISIH'] = df_dept_display['SELISIH'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_dept_display['PERSEN_REALISASI'] = df_dept_display['PERSEN_REALISASI'].apply(lambda x: f"{x:.2f}%")
    
    df_dept_display = df_dept_display.rename(columns={
        'NMDEPT': 'Kementerian',
        'PAGU_DIPA': 'Pagu',
        'REALISASI': 'Realisasi',
        'SELISIH': 'Selisih',
        'PERSEN_REALISASI': '% Realisasi'
    })
    
    st.dataframe(df_dept_display, width='stretch', hide_index=True)

# ==================== TAB 5: KEGIATAN TERBANYAK ====================
with tab5:
    st.header("Kegiatan dengan Volume Paling Banyak")

    df_kegiatan = df_filtered.groupby('NMGIAT').agg({
        'PAGU_DIPA': 'sum',
        'REALISASI': 'sum',
        'NMDEPT': 'count'
    }).reset_index().rename(columns={
        'NMDEPT': 'JUMLAH_KEGIATAN',
        'NMGIAT': 'Kegiatan'
    })
    df_kegiatan['PERSEN_REALISASI'] = (df_kegiatan['REALISASI'] / df_kegiatan['PAGU_DIPA'] * 100).replace([np.inf, -np.inf], 0).fillna(0).round(2)
    df_kegiatan = df_kegiatan.sort_values('JUMLAH_KEGIATAN', ascending=False)

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Kegiatan", int(df_kegiatan['JUMLAH_KEGIATAN'].sum()))
    with col2:
        st.metric("Total Pagu", f"Rp {df_kegiatan['PAGU_DIPA'].sum()/1e12:.2f}T")
    with col3:
        st.metric("Total Realisasi", f"Rp {df_kegiatan['REALISASI'].sum()/1e12:.2f}T")

    st.markdown("---")

    df_kegiatan_top = df_kegiatan.head(15)
    fig_kegiatan = go.Figure()
    fig_kegiatan.add_trace(go.Bar(
        x=df_kegiatan_top['JUMLAH_KEGIATAN'],
        y=df_kegiatan_top['Kegiatan'],
        orientation='h',
        marker_color='#636efa',
        name='Jumlah Kegiatan'
    ))
    fig_kegiatan.update_layout(
        title='Top 15 Kegiatan berdasarkan Jumlah Data',
        xaxis_title='Jumlah Kegiatan',
        yaxis_title='Kegiatan',
        height=600,
        margin=dict(l=240, r=20, t=60, b=20)
    )
    st.plotly_chart(fig_kegiatan, width='stretch')

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Kegiatan - Pagu dan Realisasi")
        df_kegiatan_top10 = df_kegiatan.head(10)
        fig_kegiatan_value = go.Figure()
        fig_kegiatan_value.add_trace(go.Bar(
            x=df_kegiatan_top10['PAGU_DIPA'],
            y=df_kegiatan_top10['Kegiatan'],
            name='Pagu',
            marker_color='#3498db',
            orientation='h'
        ))
        fig_kegiatan_value.add_trace(go.Bar(
            x=df_kegiatan_top10['REALISASI'],
            y=df_kegiatan_top10['Kegiatan'],
            name='Realisasi',
            marker_color='#2ecc71',
            orientation='h'
        ))
        fig_kegiatan_value.update_layout(
            barmode='group',
            xaxis_title='Nilai (Rp)',
            height=500,
            showlegend=True
        )
        st.plotly_chart(fig_kegiatan_value, width='stretch')

    with col2:
        st.subheader("Top 10 Kegiatan - Persentase Realisasi")
        df_kegiatan_pct = df_kegiatan.sort_values('PERSEN_REALISASI', ascending=False).head(10)
        fig_kegiatan_pct = go.Figure()
        fig_kegiatan_pct.add_trace(go.Bar(
            x=df_kegiatan_pct['PERSEN_REALISASI'],
            y=df_kegiatan_pct['Kegiatan'],
            marker_color=['#2ecc71' if x >= 100 else '#f59e0b' for x in df_kegiatan_pct['PERSEN_REALISASI']],
            orientation='h'
        ))
        fig_kegiatan_pct.add_vline(x=100, line_dash='dash', line_color='red')
        fig_kegiatan_pct.update_layout(
            xaxis_title='Persentase Realisasi (%)',
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_kegiatan_pct, width='stretch')

    st.markdown("---")
    st.subheader("Detail Kegiatan Terbanyak")
    df_kegiatan_display = df_kegiatan.copy()
    df_kegiatan_display['PAGU_DIPA'] = df_kegiatan_display['PAGU_DIPA'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_kegiatan_display['REALISASI'] = df_kegiatan_display['REALISASI'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_kegiatan_display['PERSEN_REALISASI'] = df_kegiatan_display['PERSEN_REALISASI'].apply(lambda x: f"{x:.2f}%")
    df_kegiatan_display = df_kegiatan_display.rename(columns={
        'JUMLAH_KEGIATAN': 'Jumlah Kegiatan',
        'PAGU_DIPA': 'Pagu',
        'REALISASI': 'Realisasi',
        'PERSEN_REALISASI': '% Realisasi'
    })
    st.dataframe(df_kegiatan_display, width='stretch', hide_index=True)

# ==================== TAB 6: BUDGET PREDICTION ====================
with tab6:
    st.header("Prediksi Budget Tahun Depan")
    
    # Prepare data for prediction
    df_pred_raw = df.groupby(['TAHUN', 'NMDEPT']).agg({
        'PAGU_DIPA': 'sum',
        'REALISASI': 'sum',
    }).reset_index()
    
    # Get max year for prediction
    max_year = df_pred_raw['TAHUN'].max()
    pred_year = max_year + 1
    
    st.info(f"📊 Prediksi budget untuk tahun **{pred_year}** berdasarkan data historis hingga tahun **{max_year}**")
    
    st.markdown("---")
    
    # Train models and make predictions
    predictions = []
    
    dept_list_pred = df_pred_raw['NMDEPT'].unique()
    
    for dept in dept_list_pred:
        df_dept_pred = df_pred_raw[df_pred_raw['NMDEPT'] == dept].sort_values('TAHUN')
        
        if len(df_dept_pred) >= 2:
            # Prepare data
            X = df_dept_pred['TAHUN'].values.reshape(-1, 1)
            y_pagu = df_dept_pred['PAGU_DIPA'].values
            y_realisasi = df_dept_pred['REALISASI'].values
            
            # Train models
            model_pagu = LinearRegression()
            model_pagu.fit(X, y_pagu)
            
            model_realisasi = LinearRegression()
            model_realisasi.fit(X, y_realisasi)
            
            # Make predictions
            X_pred = np.array([[pred_year]])
            pred_pagu = model_pagu.predict(X_pred)[0]
            pred_realisasi = model_realisasi.predict(X_pred)[0]
            
            # Ensure non-negative predictions
            pred_pagu = max(0, pred_pagu)
            pred_realisasi = max(0, pred_realisasi)
            
            pred_persen = (pred_realisasi / pred_pagu * 100) if pred_pagu > 0 else 0
            
            predictions.append({
                'NMDEPT': dept,
                'PAGU_PREDIKSI': pred_pagu,
                'REALISASI_PREDIKSI': pred_realisasi,
                'PERSEN_PREDIKSI': pred_persen
            })
    
    df_predictions = pd.DataFrame(predictions).sort_values('PAGU_PREDIKSI', ascending=False)
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Pagu Prediksi", f"Rp {df_predictions['PAGU_PREDIKSI'].sum()/1e12:.2f}T")
    with col2:
        st.metric("Total Realisasi Prediksi", f"Rp {df_predictions['REALISASI_PREDIKSI'].sum()/1e12:.2f}T")
    with col3:
        avg_pred_persen = (df_predictions['REALISASI_PREDIKSI'].sum() / df_predictions['PAGU_PREDIKSI'].sum() * 100) if df_predictions['PAGU_PREDIKSI'].sum() > 0 else 0
        st.metric("Rata-rata % Prediksi", f"{avg_pred_persen:.1f}%")
    
    st.markdown("---")
    
    # Chart: Top 15 Kementerian - Pagu Prediksi
    df_pred_top = df_predictions.head(15)
    fig_pred = go.Figure()
    fig_pred.add_trace(go.Bar(
        x=df_pred_top['PAGU_PREDIKSI'],
        y=df_pred_top['NMDEPT'],
        name='Pagu Prediksi',
        marker_color='#3498db',
        orientation='h',
        text=(df_pred_top['PAGU_PREDIKSI']/1e12).round(2),
        textposition='outside'
    ))
    fig_pred.add_trace(go.Bar(
        x=df_pred_top['REALISASI_PREDIKSI'],
        y=df_pred_top['NMDEPT'],
        name='Realisasi Prediksi',
        marker_color='#2ecc71',
        orientation='h',
        text=(df_pred_top['REALISASI_PREDIKSI']/1e12).round(2),
        textposition='outside'
    ))
    fig_pred.update_layout(
        title=f"Top 15 Kementerian - Prediksi Pagu dan Realisasi Tahun {pred_year}",
        xaxis_title="Nilai Prediksi (Rp)",
        yaxis_title="Kementerian",
        barmode='group',
        height=600,
        hovermode='x unified'
    )
    st.plotly_chart(fig_pred, width='stretch')
    
    st.markdown("---")
    
    # Historical and prediction trends for top 10 ministries
    col1, col2 = st.columns([1.5, 1.5])
    
    with col1:
        st.subheader("Trend Prediksi - Pagu (Top 5)")
        top5_depts = df_predictions.head(5)['NMDEPT'].values
        
        fig_trend_pagu = go.Figure()
        for dept in top5_depts:
            df_hist = df_pred_raw[df_pred_raw['NMDEPT'] == dept].sort_values('TAHUN')
            if len(df_hist) > 0:
                # Historical data
                fig_trend_pagu.add_trace(go.Scatter(
                    x=df_hist['TAHUN'],
                    y=df_hist['PAGU_DIPA']/1e12,
                    mode='lines+markers',
                    name=dept,
                    line=dict(width=2)
                ))
                
                # Prediction point
                if len(df_hist) >= 2:
                    pred_val = df_predictions[df_predictions['NMDEPT'] == dept]['PAGU_PREDIKSI'].values
                    if len(pred_val) > 0:
                        fig_trend_pagu.add_trace(go.Scatter(
                            x=[pred_year],
                            y=[pred_val[0]/1e12],
                            mode='markers',
                            marker=dict(size=12, symbol='diamond'),
                            name=f"{dept} (Pred)",
                            showlegend=False
                        ))
        
        fig_trend_pagu.update_layout(
            title="Trend Pagu (Historis + Prediksi)",
            xaxis_title="Tahun",
            yaxis_title="Pagu (T Rp)",
            height=450,
            hovermode='x unified'
        )
        st.plotly_chart(fig_trend_pagu, width='stretch')
    
    with col2:
        st.subheader("Trend Prediksi - Realisasi (Top 5)")
        
        fig_trend_real = go.Figure()
        for dept in top5_depts:
            df_hist = df_pred_raw[df_pred_raw['NMDEPT'] == dept].sort_values('TAHUN')
            if len(df_hist) > 0:
                # Historical data
                fig_trend_real.add_trace(go.Scatter(
                    x=df_hist['TAHUN'],
                    y=df_hist['REALISASI']/1e12,
                    mode='lines+markers',
                    name=dept,
                    line=dict(width=2)
                ))
                
                # Prediction point
                if len(df_hist) >= 2:
                    pred_val = df_predictions[df_predictions['NMDEPT'] == dept]['REALISASI_PREDIKSI'].values
                    if len(pred_val) > 0:
                        fig_trend_real.add_trace(go.Scatter(
                            x=[pred_year],
                            y=[pred_val[0]/1e12],
                            mode='markers',
                            marker=dict(size=12, symbol='diamond'),
                            name=f"{dept} (Pred)",
                            showlegend=False
                        ))
        
        fig_trend_real.update_layout(
            title="Trend Realisasi (Historis + Prediksi)",
            xaxis_title="Tahun",
            yaxis_title="Realisasi (T Rp)",
            height=450,
            hovermode='x unified'
        )
        st.plotly_chart(fig_trend_real, width='stretch')
    
    st.markdown("---")
    
    # Prediction table
    st.subheader(f"Detail Prediksi Budget Tahun {pred_year}")
    df_pred_display = df_predictions.copy()
    df_pred_display['PAGU_PREDIKSI'] = df_pred_display['PAGU_PREDIKSI'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_pred_display['REALISASI_PREDIKSI'] = df_pred_display['REALISASI_PREDIKSI'].apply(lambda x: f"Rp {x/1e12:.2f}T")
    df_pred_display['PERSEN_PREDIKSI'] = df_pred_display['PERSEN_PREDIKSI'].apply(lambda x: f"{x:.2f}%")
    
    df_pred_display = df_pred_display.rename(columns={
        'NMDEPT': 'Kementerian',
        'PAGU_PREDIKSI': f'Pagu Prediksi {pred_year}',
        'REALISASI_PREDIKSI': f'Realisasi Prediksi {pred_year}',
        'PERSEN_PREDIKSI': f'% Prediksi {pred_year}'
    })
    
    st.dataframe(df_pred_display, width='stretch', hide_index=True)
    
    st.info(f"📌 **Catatan Metodologi**: Prediksi menggunakan model regresi linear yang dilatih berdasarkan data historis. Presisi prediksi bergantung pada konsistensi trend data masa lalu.")

    # Footer
    st.markdown("---")
    st.markdown(f"*Dashboard Realisasi Belanja Kementerian | Data terakhir diperbarui: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}*")

except Exception as e:
    st.error(f"""
❌ **Unexpected Error Occurred!**

**Error Details:**
```
{traceback.format_exc()}
```

**Troubleshooting:**
1. Check if data file exists: `git ls-files | grep Belanja`
2. Verify recent commits: `git log --oneline | head -5`
3. Check Streamlit Cloud logs for more details
4. Try: `git push -f origin main` to force redeploy
    """)
    st.stop()
