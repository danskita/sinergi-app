import streamlit as st
from supabase import create_client, Client
import guru
import ortu

st.set_page_config(page_title="Sinergi - Penghubung Orang Tua & Guru", page_icon="🤝", layout="wide")

@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_connection()
st.session_state['supabase'] = supabase

# ==========================================
# MASTER KURIKULUM TKA / TPA
# ==========================================
if 'kurikulum' not in st.session_state:
    st.session_state['kurikulum'] = {
        "Iqro 1": {
            "sholat": ["Do'a Iftitah", "Surah Al Fatihah", "Do'a Ruku & Sujud", "Praktik Wudhu & Sholat", "Do'a Setelah Wudhu"],
            "doa": ["Do'a dan Adab Belajar", "Do'a Mensyukuri Nikmat", "Do'a dan Adab Sebelum Makan", "Do'a dan Adab Sesudah Makan"],
            "surah": ["QS An Naas", "QS Al Falaq", "QS Al Ikhlash", "QS Al Lahab"],
            "hadist": ["Hadist Kebersihan", "Hadist Senyum", "Hadist Larangan Marah"]
        },
        "Iqro 2": {
            "sholat": ["Do'a I'tidal", "Do'a Duduk Diantara 2 Sujud", "Do'a Tasyahud", "Praktik Wudhu & Sholat", "Do'a Setelah Wudhu"],
            "doa": ["Do'a dan Adab Sebelum Tidur", "Do'a dan Adab Bangun Tidur", "Do'a dan Adab Masuk WC", "Do'a dan Adab Keluar WC"],
            "surah": ["QS An Nashr", "QS Al Kautsar", "QS Al 'Ashr", "QS Al Kafirun"],
            "hadist": ["Hadist Niat", "Hadist Mencintai Keindahan", "Hadist Menyebarkan Salam"]
        },
        "Iqro 3": {
            "sholat": ["Sholawat", "Do'a Sebelum Salam", "Salam", "Dzikir Setelah Sholat", "Praktik Wudhu & Sholat", "Do'a Setelah Wudhu"],
            "doa": ["Do'a dan Adab Masuk Rumah", "Do'a dan Adab Keluar Rumah", "Do'a dan Adab Berpakaian", "Do'a dan Adab Melepas Pakaian"],
            "surah": ["QS Al Ma'un", "QS Quraisy", "QS Al Fil", "QS Al Humazah", "QS At Takatsur"],
            "hadist": ["Hadist Menjaga Lisan", "Hadist Makan/Minum Tangan Kanan", "Hadist Bersikap Lemah Lembut"]
        },
        "Iqro 4": {
            "sholat": ["QS Al Baqarah ayat 255 (Ayat Qursiy)", "QS Al Mu'minun 1-11", "QS Ar Rahman 1-15"], 
            "doa": ["Do'a Kebaikan Dunia Akhirat", "Do'a dan Adab Bercermin", "Senandung Do'a Al-Qur'an", "Do'a dan Adab Naik Kendaraan", "Do'a Memperoleh Rahmat"],
            "surah": ["QS Al Qari'ah", "QS Al 'Aadiyyat", "QS Al Zalzalah", "QS Al Bayyinah", "QS Al Qadr"],
            "hadist": ["Hadist Sesama Muslim Bersaudara", "Hadist Tolonglah Saudaramu", "Hadist Larangan Mencela Makanan"]
        },
        "Iqro 5": {
            "sholat": ["QS Al Baqarah 284-286", "QS Al Jumu'ah 9-11", "QS Luqman 12-19"],
            "doa": ["Do'a Kedua Orang Tua", "Do'a dan Adab Akhir Pertemuan", "Do'a dan Adab Masuk Masjid", "Do'a dan Adab Keluar Masjid"],
            "surah": ["QS Al Alaq", "QS At Tin", "QS Al Insyirah", "QS Ad Dhuha", "QS Al Lail"],
            "hadist": ["Hadist Berbuat Baik", "Hadist Kasih Sayang", "Hadist Keutamaan Membaca Al-Qur'an"]
        },
        "Iqro 6": {
            "sholat": ["QS Al Fath 28-29", "QS Ali Imran 133-136", "QS An Nahl 65-69"],
            "doa": ["Do'a Sesudah Adzan", "Do'a Ketika Sakit", "Do'a Menjenguk Orang Sakit", "Do'a Kesehatan & Akhlak Baik", "Do'a Dzikir Pagi & Sore Hari"],
            "surah": ["QS As Syams", "QS Al Balad", "QS Al Fajr", "QS Al Ghasyiah", "QS Al A'la"],
            "hadist": ["Hadist Larangan Minum Berdiri", "Hadist Perkataan Baik Adalah Sedekah", "Hadist Amal Paling Utama", "Hadist Berbakti Pada Orang Tua"]
        }
    }

# ==========================================
# SISTEM LOGIN & PENDAFTARAN (3 TAB)
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'role': '', 'username': '', 'kelas_admin': '', 'id_lembaga': ''})

def halaman_otentikasi():
    st.markdown("""
    <div style="text-align: center; border-bottom: 2px solid #2E7D32; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="color: #2E7D32; margin-bottom: 0;">🤝 Sinergi</h1>
        <p style="font-size: 16px; color: #555; margin-top: 5px; font-weight: bold;">Aplikasi Penghubung Orang Tua dan Guru</p>
    </div>
    """, unsafe_allow_html=True)
    
    # HANYA lembaga yang berstatus "Verified" yang bisa dipilih di pendaftaran santri
    res_lembaga = supabase.table('info_lembaga').select('*').eq('status', 'Verified').execute()
    daftar_lembaga = {l['nama_lembaga']: l['id_lembaga'] for l in res_lembaga.data} if res_lembaga.data else {}
    
    tab_login, tab_daftar_santri, tab_daftar_lembaga = st.tabs([
        "🔐 Masuk (Login)", 
        "📝 Daftar Santri Baru", 
        "🏛️ Daftarkan Lembaga / TPQ Baru"
    ])
    
    # --- TAB 1: LOGIN ---
    with tab_login:
        st.info("💡 **Contoh Akun:**\n- Ortu: **mama adi** (Pass: 123)\n- Guru: **admin tka a** (Pass: 123)")
        peran = st.radio("Masuk Sebagai:", ["Orang Tua", "Admin / Guru"], horizontal=True)
        username = st.text_input("Username").strip().lower() 
        password = st.text_input("Password", type="password")
        
        if st.button("Masuk Aplikasi", use_container_width=True):
            if peran == "Orang Tua":
                response = supabase.table('santri').select('*').eq('username', username).execute()
                data_user = response.data
                if len(data_user) > 0 and data_user[0]['password'] == password:
                    id_lmbg = data_user[0].get('id_lembaga', '')
                    st.session_state.update({'logged_in': True, 'role': 'ortu', 'username': username, 'id_lembaga': id_lmbg, 'user_data': data_user[0]})
                    st.rerun()
                else: st.error("Username atau Password Orang Tua salah!")
            
            elif peran == "Admin / Guru":
                response = supabase.table('admin_kelas').select('*').eq('username', username).execute()
                data_admin = response.data
                if len(data_admin) > 0 and data_admin[0]['password'] == password:
                    id_lmbg = data_admin[0].get('id_lembaga', '')
                    # Cek apakah lembaga guru ini sudah diverifikasi Super Admin
                    cek_lembaga = supabase.table('info_lembaga').select('status').eq('id_lembaga', id_lmbg).execute()
                    status_lmbg = cek_lembaga.data[0].get('status', 'Verified') if cek_lembaga.data else 'Verified'
                    
                    if status_lmbg == 'Pending':
                        st.warning("⏳ **Lembaga Anda sedang menunggu verifikasi dari Super Admin.**\nSilakan coba login kembali setelah pendaftaran lembaga Anda disetujui.")
                    else:
                        st.session_state.update({'logged_in': True, 'role': 'guru', 'username': username, 'id_lembaga': id_lmbg, 'kelas_admin': data_admin[0]['kelas']})
                        st.rerun()
                else: st.error("Username atau Password Admin salah!")

    # --- TAB 2: DAFTAR SANTRI BARU (UNTUK ORTU) ---
    with tab_daftar_santri:
        st.info("Pendaftaran khusus Orang Tua Santri pada lembaga yang telah terverifikasi.")
        with st.form("form_pendaftaran_santri"):
            pilihan_nama_lmbg = st.selectbox("Pilih Lembaga / TPQ / Sekolah Anak", list(daftar_lembaga.keys()) if daftar_lembaga else ["Belum ada lembaga terverifikasi"])
            nama_panggilan = st.text_input("Nama Panggilan Anak", placeholder="Cth: Budi")
            kelas_anak = st.selectbox("Pilih Kelas Anak", ["TKA A", "TKA B", "TPA A", "TPA B"])
            pass_baru = st.text_input("Buat Password", value="123", type="password")
            pass_konfirm = st.text_input("Konfirmasi Password", value="123", type="password")
            
            if st.form_submit_button("Daftar Akun Santri", use_container_width=True):
                if not daftar_lembaga: st.error("Belum ada lembaga yang tersedia di sistem.")
                elif not nama_panggilan.strip(): st.error("Nama panggilan wajib diisi!")
                elif pass_baru != pass_konfirm: st.error("Password tidak cocok!")
                else:
                    base_username = f"mama {nama_panggilan.strip().lower()}"
                    username_final = base_username
                    counter = 1
                    while True:
                        cek_user = supabase.table('santri').select('username').eq('username', username_final).execute()
                        if len(cek_user.data) == 0: break
                        username_final = f"{base_username} {counter}"
                        counter += 1
                    
                    id_lmbg_terpilih = daftar_lembaga[pilihan_nama_lmbg]
                    data_baru = {
                        "username": username_final, "password": pass_baru,
                        "nama_panggilan": nama_panggilan.strip(), "kelas": kelas_anak,
                        "id_lembaga": id_lmbg_terpilih,
                        "biodata_lengkap": False, "reward_khusus": "-",
                        "capaian": {"surah": [], "doa": [], "hadist": [], "sholat": []}
                    }
                    supabase.table('santri').insert(data_baru).execute()
                    st.success(f"✅ Akun berhasil dibuat! Username Anda: **{username_final}**")

    # --- TAB 3: DAFTAR LEMBAGA BARU (MENUNGGU VERIFIKASI) ---
    with tab_daftar_lembaga:
        st.info("📌 Daftarkan sekolah/TPQ Anda. Pengajuan akan diproses & diverifikasi oleh Super Admin.")
        with st.form("form_pendaftaran_lembaga"):
            st.subheader("1. Identitas Lembaga / Sekolah")
            id_lmbg_input = st.text_input("ID Lembaga (Tanpa spasi, huruf kecil)", placeholder="Cth: tpq_al_hidayah")
            nama_lmbg_input = st.text_input("Nama Resmi Lembaga / TPQ", placeholder="Cth: TPQ AL-HIDAYAH BANDUNG")
            alamat_lmbg_input = st.text_area("Alamat Lengkap Lembaga")
            
            st.markdown("---")
            st.subheader("2. Akun Admin / Guru Utama (Untuk Login Pertama)")
            user_guru_input = st.text_input("Username Admin Guru", placeholder="Cth: admin_alhidayah")
            pass_guru_input = st.text_input("Password Admin", value="123", type="password")
            kelas_guru_input = st.selectbox("Kelas yang Dipegang Admin Ini", ["TKA A", "TKA B", "TPA A", "TPA B"])
            
            if st.form_submit_button("Ajukan Pendaftaran Lembaga", use_container_width=True):
                clean_id = id_lmbg_input.strip().lower().replace(" ", "_")
                clean_user = user_guru_input.strip().lower()
                
                # Cek apakah ID lembaga atau username sudah dipakai
                cek_id = supabase.table('info_lembaga').select('id_lembaga').eq('id_lembaga', clean_id).execute()
                cek_usr = supabase.table('admin_kelas').select('username').eq('username', clean_user).execute()
                
                if not clean_id or not nama_lmbg_input.strip() or not clean_user:
                    st.error("Semua kolom utama wajib diisi!")
                elif len(cek_id.data) > 0:
                    st.error("ID Lembaga tersebut sudah terdaftar! Gunakan ID lain.")
                elif len(cek_usr.data) > 0:
                    st.error("Username admin tersebut sudah digunakan! Gunakan username lain.")
                else:
                    # 1. Simpan lembaga baru dengan status "Pending" (Menunggu Verifikasi)
                    supabase.table('info_lembaga').insert({
                        "id_lembaga": clean_id,
                        "nama_lembaga": nama_lmbg_input.strip(),
                        "alamat_lembaga": alamat_lmbg_input.strip(),
                        "status": "Pending"
                    }).execute()
                    
                    # 2. Simpan akun admin guru perdana
                    supabase.table('admin_kelas').insert({
                        "username": clean_user,
                        "password": pass_guru_input,
                        "kelas": kelas_guru_input,
                        "id_lembaga": clean_id,
                        "status": "Pending"
                    }).execute()
                    
                    st.success(f"🎉 **Pengajuan Berhasil!**\nLembaga **{nama_lmbg_input}** telah dikirim ke Super Admin.\nAnda dapat masuk setelah status pengajuan Anda disetujui/diverifikasi.")

if not st.session_state['logged_in']:
    halaman_otentikasi()
else:
    if st.session_state['role'] == 'ortu': ortu.tampilkan_dashboard()
    elif st.session_state['role'] == 'guru': guru.tampilkan_dashboard()