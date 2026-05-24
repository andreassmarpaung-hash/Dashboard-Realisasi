# 📊 Dashboard Realisasi Belanja Kementerian

Dashboard interaktif untuk visualisasi dan analisis realisasi belanja kementerian dengan fitur filtering yang komprehensif.

## ✨ Fitur Utama

### 1️⃣ Realisasi vs Pagu per Tahun
- Perbandingan total pagu dan realisasi untuk seluruh kementerian
- Visualisasi trend realisasi berdasarkan tahun
- Menampilkan persentase realisasi dan selisih
- Metrics overview: Total Pagu, Total Realisasi, Persentase, dan Selisih

### 2️⃣ Realisasi per Wilayah
- Breakdown realisasi berdasarkan lokasi geografis
- Top 15 wilayah dengan realisasi tertinggi
- Perbandingan pagu vs realisasi per wilayah
- Tabel lengkap semua wilayah dengan sorting

### 3️⃣ Indikator Early Warning
- **Sistem peringatan dini untuk item yang exceeding budget**
- Identifikasi item dengan realisasi melebihi pagu
- Filter dinamis berdasarkan minimum selisih
- Menampilkan Top 20 item over budget
- Tabel detail dengan breakdown per kementerian, wilayah, dan kegiatan

### 4️⃣ Realisasi per Kementerian
- Analisis realisasi untuk setiap kementerian/lembaga
- Scatter plot hubungan pagu vs realisasi
- Top 10 kementerian berdasarkan volume realisasi
- Persentase realisasi dengan visual indikator
- Tabel komprehensif dengan sorting dan filtering

## 🔍 Filter Data

Dashboard dilengkapi dengan filter sidebar untuk:
- **Tahun**: Pilih satu atau multiple tahun
- **Kementerian**: Filter berdasarkan institusi
- **Lokasi/Wilayah**: Filter berdasarkan area geografis

Semua filter bekerja secara real-time dan terintegrasi dengan semua visualisasi.

## 🚀 Cara Menjalankan

### Opsi 1: Menggunakan Script Shell
```bash
cd /Users/djpb/Documents/Dashboard\ Realisasi/
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Opsi 2: Manual Installation & Run
```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run dashboard.py
```

Dashboard akan membuka di browser pada URL: `http://localhost:8501`

## 📋 Requirements

- Python 3.8+
- Streamlit 1.28.1
- Pandas 2.0.3
- Plotly 5.17.0
- NumPy 1.24.3

## 📊 Visualisasi

Dashboard menggunakan berbagai jenis visualisasi:
- **Bar Charts**: Perbandingan data antar kategori
- **Line Charts**: Trend analysis
- **Scatter Plots**: Hubungan antar variabel
- **Tables**: Data detail dengan formatting currency

## 💡 Tips Penggunaan

1. **Real-time Filtering**: Gunakan sidebar untuk filter data yang ingin dilihat
2. **Export Data**: Klik kanan pada chart untuk download as PNG
3. **Hover Info**: Hover mouse pada chart untuk melihat detail data
4. **Sortable Tables**: Klik header column untuk sorting

## 📁 File Structure

```
Dashboard Realisasi/
├── Belanja_Full_Baru.csv    # Data source
├── dashboard.py              # Main dashboard application
├── requirements.txt          # Python dependencies
├── run_dashboard.sh          # Script untuk menjalankan
└── README.md                 # Documentation (this file)
```

## 🎨 Color Coding

- 🔵 **Biru**: Data Pagu
- 🟢 **Hijau**: Realisasi Normal/Positif
- 🔴 **Merah**: Over Budget/Warning
- 🟡 **Kuning**: Area Caution

## 📞 Support

Jika ada pertanyaan atau isu, silakan periksa:
1. Pastikan Python 3.8+ terinstall
2. Pastikan semua dependencies terinstall dengan benar
3. Pastikan CSV file ada di lokasi yang tepat
4. Cek bahwa port 8501 tidak digunakan aplikasi lain

---
*Last Updated: May 24, 2026*
