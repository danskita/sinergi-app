import streamlit as st
import datetime

def tampilkan_dashboard():
    # Mengambil jembatan koneksi Supabase dari app.py
    supabase = st.session_state['supabase']
    username = st.session_state['username']
    
    # 1. AMBIL DATA SANTRI DARI DATABASE CLOUD
    user_res = supabase.table('santri').select('*').eq('username', username).execute()
    
    if not user_res.data:
        st.error("Data tidak ditemukan di Database.")
        return
        
    user_data = user_res.data[0]
    
    # 2. PENGUNCI LAYAR (FORM BIODATA)
    if not user_data.get("biodata_lengkap", False):
        st.warning("⚠️ Wajib melengkapi Biodata Resmi sesuai KK/KTP sebelum mengakses rapor.")
        with st.form("form_biodata"):
            nama_lengkap = st.text_input("Nama Lengkap Anak (Sesuai KK)")
            nik_anak = st.text_input("NIK Anak")
            ttl = st.text_input("Tempat, Tanggal Lahir")
            nama_ayah = st.text_input("Nama Ayah")
            nama_ibu = st.text_input("Nama Ibu")
            no_hp = st.text_input("Nomor HP/WhatsApp Aktif (Penting untuk pengiriman rapor WA)")
                
            if st.form_submit_button("Simpan Biodata Permanen", use_container_width=True):
                if not nama_lengkap or not nama_ayah or not nama_ibu or not no_hp:
                    st.error("Mohon lengkapi data utama (termasuk No HP).")
                else:
                    # Update data ke Supabase
                    supabase.table('santri').update({
                        "biodata_lengkap": True,
                        "nama_lengkap": nama_lengkap,
                        "nik_anak": nik_anak,
                        "ttl": ttl,
                        "nama_ayah": nama_ayah,
                        "nama_ibu": nama_ibu,
                        "no_hp": no_hp
                    }).eq('username', username).execute()
                    
                    st.success("Biodata berhasil disimpan di Cloud!")
                    st.rerun()
                    
        if st.button("Keluar", type="primary"):
            st.session_state.update({'logged_in': False, 'role': '', 'username': ''})
            st.rerun()
            
    # 3. DASBOR UTAMA ORANG TUA
    else:
        # Mengambil Laporan Harian Terakhir dari Database
        laporan_res = supabase.table('laporan_harian').select('*').eq('username_santri', username).order('created_at', desc=True).limit(1).execute()
        laporan = laporan_res.data[0] if laporan_res.data else {}
        
        nama_tampil = user_data.get("nama_lengkap") or user_data.get("nama_panggilan")
        
        st.title(f"Laporan: {nama_tampil}")
        st.caption(f"📅 Tanggal: {laporan.get('tanggal', '-')} | 📍 Kelas: {user_data.get('kelas', '-')}")
        st.markdown("---")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Laporan Harian", "📈 Progres Hafalan", "💬 Buku Penghubung", "📊 Rekap Bulanan", "📋 Profil Anak"])
        
        with tab1:
            status_hadir = laporan.get('kehadiran', '-')
            if status_hadir == "Hadir": st.success(f"**Kehadiran:** {status_hadir}")
            elif status_hadir in ["Sakit", "Izin"]: st.warning(f"**Kehadiran:** {status_hadir}")
            elif status_hadir == "Alpa": st.error(f"**Kehadiran:** {status_hadir}")
            
            narasi = laporan.get('narasi_laporan', '-')
            if narasi == "-" or not narasi: 
                st.info("Belum ada evaluasi dari Ustadz/Ustadzah hari ini.")
            else:
                st.info(narasi)
                if not laporan.get('status_murojaah', False):
                    if st.button("✅ Tandai Sudah Murojaah di Rumah", use_container_width=True):
                        # Update status murojaah ke tabel Laporan di Supabase
                        supabase.table('laporan_harian').update({"status_murojaah": True}).eq('id', laporan['id']).execute()
                        st.rerun()
                else:
                    st.success("🎉 Anda telah mengkonfirmasi Murojaah hari ini!")

        with tab2:
            st.write("Silakan pilih Jilid Iqro anak untuk melihat target kurikulum dan status pencapaiannya.")
            cek_jilid = st.selectbox("Lihat Target Kurikulum Jilid:", ["Iqro 1", "Iqro 2", "Iqro 3", "Iqro 4", "Iqro 5", "Iqro 6"])
            
            target_kurikulum = st.session_state['kurikulum'][cek_jilid]
            capaian_anak = user_data.get("capaian", {"surah": [], "doa": [], "hadist": [], "sholat": []})
            if capaian_anak is None: capaian_anak = {"surah": [], "doa": [], "hadist": [], "sholat": []}
            
            st.markdown("---")
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("🌟 **Target Surah:**")
                for item in target_kurikulum["surah"]:
                    if item in capaian_anak.get("surah", []): st.success(f"✅ {item} *(Lulus)*")
                    else: st.warning(f"⏳ {item} *(Sedang Proses)*")
                
                st.write("📜 **Target Hadist:**")
                for item in target_kurikulum["hadist"]:
                    if item in capaian_anak.get("hadist", []): st.success(f"✅ {item} *(Lulus)*")
                    else: st.warning(f"⏳ {item} *(Sedang Proses)*")
                    
            with col_b:
                st.write("🤲 **Target Do'a:**")
                for item in target_kurikulum["doa"]:
                    if item in capaian_anak.get("doa", []): st.success(f"✅ {item} *(Lulus)*")
                    else: st.warning(f"⏳ {item} *(Sedang Proses)*")
                    
                st.write("🕋 **Target Sholat/Ayat:**")
                for item in target_kurikulum["sholat"]:
                    if item in capaian_anak.get("sholat", []): st.success(f"✅ {item} *(Lulus)*")
                    else: st.warning(f"⏳ {item} *(Sedang Proses)*")

        with tab3:
            # Menarik data Chat dari Supabase
            chat_res = supabase.table('buku_penghubung').select('*').eq('username_santri', username).order('created_at', desc=False).execute()
            for pesan in chat_res.data:
                if pesan["pengirim"] == "Orang Tua": st.info(f"**Anda** ({pesan['waktu_kirim']}):\n\n{pesan['isi_pesan']}")
                else: st.success(f"**Ustaz/Ustazah** ({pesan['waktu_kirim']}):\n\n{pesan['isi_pesan']}")
                    
            with st.form("form_chat_ortu"):
                pesan_baru = st.text_area("Tulis pesan:")
                if st.form_submit_button("Kirim") and pesan_baru.strip():
                    supabase.table('buku_penghubung').insert({
                        "username_santri": username,
                        "pengirim": "Orang Tua",
                        "waktu_kirim": datetime.datetime.now().strftime("%d %B %Y - %H:%M"),
                        "isi_pesan": pesan_baru
                    }).execute()
                    st.rerun()
                    
        with tab4:
            st.subheader("📊 Rekapitulasi Kehadiran")
            
            # Hitung Rekap Otomatis dari Tabel Laporan
            bulan_res = supabase.table('laporan_harian').select('bulan_tahun').eq('username_santri', username).execute()
            daftar_bulan = list(set([item['bulan_tahun'] for item in bulan_res.data])) if bulan_res.data else []
            
            if not daftar_bulan: 
                st.info("Belum ada data riwayat kehadiran bulanan.")
            else:
                pilih_bulan = st.selectbox("Pilih Bulan", sorted(daftar_bulan, reverse=True))
                
                # Query menghitung jumlah kehadiran di bulan tersebut
                rekap_hadir = len(supabase.table('laporan_harian').select('id').eq('username_santri', username).eq('bulan_tahun', pilih_bulan).eq('kehadiran', 'Hadir').execute().data)
                rekap_sakit = len(supabase.table('laporan_harian').select('id').eq('username_santri', username).eq('bulan_tahun', pilih_bulan).eq('kehadiran', 'Sakit').execute().data)
                rekap_izin = len(supabase.table('laporan_harian').select('id').eq('username_santri', username).eq('bulan_tahun', pilih_bulan).eq('kehadiran', 'Izin').execute().data)
                rekap_alpa = len(supabase.table('laporan_harian').select('id').eq('username_santri', username).eq('bulan_tahun', pilih_bulan).eq('kehadiran', 'Alpa').execute().data)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Hadir", rekap_hadir)
                col2.metric("Sakit", rekap_sakit)
                col3.metric("Izin", rekap_izin)
                col4.metric("Alpa", rekap_alpa)
                    
        with tab5:
            st.write(f"**Kelas:** {user_data.get('kelas', '-')}")
            st.write(f"**Nama Lengkap:** {user_data.get('nama_lengkap', '-')}")
            st.write(f"**Nomor HP/WA:** {user_data.get('no_hp', '-')}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Keluar (Logout)", type="primary"):
            st.session_state.update({'logged_in': False, 'role': '', 'username': ''})
            st.rerun()