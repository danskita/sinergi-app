import streamlit as st

def tampilkan_dashboard():
    supabase = st.session_state['supabase']
    
    st.title("🛡️ Pusat Pengendali Super Admin")
    st.subheader("Manajemen Daftar Lembaga / TPQ / Sekolah & Akun Guru")
    
    tab_lembaga, tab_guru = st.tabs(["🏛️ Kelola Lembaga", "👨‍🏫 Kelola Akun Guru"])
    
    # ==========================================
    # TAB 1: MANAJEMEN LEMBAGA
    # ==========================================
    with tab_lembaga:
        res_lmbg = supabase.table('info_lembaga').select('*').execute()
        list_lembaga = res_lmbg.data if res_lmbg.data else []
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("🏛️ Daftar Lembaga Terdaftar")
            if not list_lembaga:
                st.info("Belum ada lembaga yang terdaftar.")
            else:
                for lmbg in list_lembaga:
                    badge_status = "🟢 AKTIF" if lmbg.get('status') == 'Verified' else "🟡 MENUNGGU VERIFIKASI"
                    with st.expander(f"📌 {lmbg['nama_lembaga']} | {badge_status} (ID: {lmbg['id_lembaga']})"):
                        st.write(f"**Alamat:** {lmbg['alamat_lembaga']}")
                        if st.button("🗑️ Hapus Lembaga Ini", key=f"del_{lmbg['id_lembaga']}"):
                            supabase.table('info_lembaga').delete().eq('id_lembaga', lmbg['id_lembaga']).execute()
                            st.success(f"Lembaga {lmbg['nama_lembaga']} berhasil dihapus!")
                            st.rerun()

        with col2:
            st.subheader("➕ Tambah Lembaga Baru")
            with st.form("form_tambah_lembaga"):
                id_lmbg_baru = st.text_input("ID Unik Lembaga (Tanpa Spasi)", placeholder="Cth: tpq_assalam")
                nama_lmbg_baru = st.text_input("Nama Lembaga / TPQ", placeholder="Cth: TPQ AS-SALAM JAKARTA")
                alamat_lmbg_baru = st.text_area("Alamat Lengkap")
                
                if st.form_submit_button("Simpan Lembaga Baru", use_container_width=True):
                    if not id_lmbg_baru.strip() or not nama_lmbg_baru.strip():
                        st.error("ID dan Nama Lembaga wajib diisi!")
                    else:
                        clean_id = id_lmbg_baru.strip().lower().replace(" ", "_")
                        supabase.table('info_lembaga').insert({
                            "id_lembaga": clean_id,
                            "nama_lembaga": nama_lmbg_baru.strip(),
                            "alamat_lembaga": alamat_lmbg_baru.strip(),
                            "status": "Verified"  # <-- DITAMBAHKAN AGAR LANGSUNG AKTIF
                        }).execute()
                        st.success("✅ Lembaga baru berhasil ditambahkan!")
                        st.rerun()
                        
    # ==========================================
    # TAB 2: BUAT AKUN GURU UNTUK LEMBAGA
    # ==========================================
    with tab_guru:
        st.subheader("➕ Buat Akun Guru/Admin Baru untuk Lembaga")
        st.caption("Super Admin dapat membuat akun login untuk ustadz/ustadzah di setiap lembaga.")
        
        # Hanya ambil lembaga yang sudah diverifikasi
        res_lmbg = supabase.table('info_lembaga').select('*').eq('status', 'Verified').execute()
        map_lembaga = {l['nama_lembaga']: l['id_lembaga'] for l in res_lmbg.data} if res_lmbg.data else {}
        
        if not map_lembaga:
            st.warning("Silakan tambah lembaga terlebih dahulu di tab sebelah sebelum membuat akun guru.")
        else:
            with st.form("form_buat_guru"):
                pilih_lmbg = st.selectbox("Pilih Lembaga", list(map_lembaga.keys()))
                user_guru = st.text_input("Username Guru (Untuk Login)", placeholder="Cth: ustadz_ahmad")
                pass_guru = st.text_input("Password Guru", value="123")
                kelas_guru = st.selectbox("Kelompok / Kelas yang Dipegang", ["TKA A", "TKA B", "TPA A", "TPA B"])
                
                if st.form_submit_button("Buat Akun Guru", use_container_width=True):
                    if not user_guru.strip():
                        st.error("Username guru wajib diisi!")
                    else:
                        supabase.table('admin_kelas').insert({
                            "username": user_guru.strip().lower(),
                            "password": pass_guru,
                            "kelas": kelas_guru,
                            "id_lembaga": map_lembaga[pilih_lmbg],
                            "status": "Active"  # <-- DITAMBAHKAN AGAR GURU BISA LANGSUNG LOGIN
                        }).execute()
                        st.success(f"✅ Akun guru '{user_guru}' untuk {pilih_lmbg} berhasil dibuat!")

    st.markdown("---")
    if st.button("Keluar dari Super Admin (Logout)", type="primary"):
        st.session_state.update({'logged_in': False, 'role': '', 'username': ''})
        st.rerun()