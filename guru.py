import streamlit as st
import datetime
import urllib.parse

def tampilkan_dashboard():
    # Mengambil jembatan koneksi Supabase & Kurikulum dari app.py
    supabase = st.session_state['supabase']
    kelas_saya = st.session_state.get('kelas_admin', 'Admin')
    kurikulum = st.session_state['kurikulum']
    
    st.title(f"👨‍🏫 Dasbor Guru - Kelas {kelas_saya}")
    
    # 1. AMBIL DATA SANTRI KELAS INI DARI DATABASE CLOUD
    res_santri = supabase.table('santri').select('*').eq('kelas', kelas_saya).execute()
    data_santri_list = res_santri.data
    
    map_nama_ke_username = {}
    for data in data_santri_list:
        nama_lengkap = data.get("nama_lengkap") or data.get("nama_panggilan", "Santri")
        nama_tampil = f"{nama_lengkap} ({data.get('nama_panggilan', '')})" if data.get("biodata_lengkap") else f"❓ {data.get('nama_panggilan', '')} (Belum Biodata)"
        map_nama_ke_username[nama_tampil] = data['username']
            
    daftar_nama_anak = list(map_nama_ke_username.keys())
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Input Laporan", "📈 Progres Kurikulum", "💬 Buku Penghubung", "📅 Rekap Kehadiran", "📁 Data Kelas"])
    
    if not daftar_nama_anak:
        st.warning(f"Belum ada santri yang mendaftar di kelas {kelas_saya}.")
        st.stop()
        
    # --- TAB 1: INPUT LAPORAN ---
    with tab1:
        col_a, col_b = st.columns(2)
        with col_a: pilih_santri_laporan = st.selectbox("1. Pilih Santri", daftar_nama_anak)
        with col_b: input_jilid = st.selectbox("2. Posisi Bacaan Anak", ["-", "Iqro 1", "Iqro 2", "Iqro 3", "Iqro 4", "Iqro 5", "Iqro 6", "Al-Qur'an"])
        
        username_terpilih = map_nama_ke_username[pilih_santri_laporan]
        # Cari data detail santri yang sedang dipilih
        user_data = next((item for item in data_santri_list if item["username"] == username_terpilih), {})
        nama_panggilan = user_data.get('nama_panggilan', 'Ananda')
        
        materi_tersedia = kurikulum.get(input_jilid, {"sholat": [], "doa": [], "surah": [], "hadist": []})
        opt_surah = ["-"] + materi_tersedia["surah"] + ["Lainnya (Ketik Manual)"]
        opt_doa = ["-"] + materi_tersedia["doa"] + ["Lainnya (Ketik Manual)"]
        opt_sholat = ["-"] + materi_tersedia["sholat"] + ["Lainnya (Ketik Manual)"]
        opt_hadist = ["-"] + materi_tersedia["hadist"] + ["Lainnya (Ketik Manual)"]
        
        with st.form("form_laporan"):
            st.subheader("📍 Kehadiran")
            input_kehadiran = st.radio("Status Kehadiran", ["Hadir", "Sakit", "Izin", "Alpa"], horizontal=True)
            st.markdown("---")
            
            st.subheader("📖 1. Laporan Membaca (Iqro/Al-Qur'an)")
            col1, col2 = st.columns(2)
            with col1: input_hal = st.text_input("Halaman", placeholder="Cth: Hal 15")
            with col2: input_status_baca = st.radio("Status Bacaan", ["Lancar", "Mengulang"])
            input_huruf_sulit = st.text_input("Kendala Huruf (Bila ada)", placeholder="Cth: Masih tertukar huruf Ja dan Kho")
            st.markdown("---")
            
            st.subheader("🧠 2. Target Kurikulum (Surah, Do'a & Hadist)")
            c_surah, c_doa = st.columns(2)
            with c_surah:
                target_surah = st.selectbox("Surah Pendek", opt_surah)
                manual_surah = st.text_input("Ketik Surah", key="ms")
                status_surah = st.radio("Evaluasi Surah", ["Lancar 🌟", "Perlu Murojaah"], horizontal=True)
            with c_doa:
                target_doa = st.selectbox("Do'a Harian", opt_doa)
                manual_doa = st.text_input("Ketik Do'a", key="md")
                status_doa = st.radio("Evaluasi Do'a", ["Lancar 🌟", "Perlu Murojaah"], horizontal=True)
                
            c_hadist, c_sholat = st.columns(2)
            with c_hadist:
                target_hadist = st.selectbox("Hafalan Hadist", opt_hadist)
                manual_hadist = st.text_input("Ketik Hadist", key="mh")
                status_hadist = st.radio("Evaluasi Hadist", ["Lancar 🌟", "Perlu Murojaah"], horizontal=True)
            with c_sholat:
                target_sholat = st.selectbox("Bacaan Sholat", opt_sholat)
                manual_sholat = st.text_input("Ketik Bacaan", key="msh")
                status_sholat = st.radio("Evaluasi Bacaan", ["Lancar 🌟", "Perlu Murojaah"], horizontal=True)
            
            st.markdown("---")
            st.subheader("🌱 3. Akhlak & Catatan")
            col8, col9 = st.columns(2)
            with col8: input_fokus = st.selectbox("Fokus Belajar", ["-", "Sangat Baik", "Baik", "Kurang Fokus"])
            with col9: input_adab = st.selectbox("Adab / Sikap", ["-", "Sangat Baik", "Baik", "Tantangan"])
            input_catatan = st.text_area("Pesan Tambahan (Opsional)")
            
            if st.form_submit_button("Simpan & Kirim Laporan", use_container_width=True):
                s_final = manual_surah if target_surah == "Lainnya (Ketik Manual)" else target_surah
                d_final = manual_doa if target_doa == "Lainnya (Ketik Manual)" else target_doa
                h_final = manual_hadist if target_hadist == "Lainnya (Ketik Manual)" else target_hadist
                sh_final = manual_sholat if target_sholat == "Lainnya (Ketik Manual)" else target_sholat
                
                # Mengupdate Capaian Lulus
                capaian = user_data.get("capaian") or {"surah": [], "doa": [], "hadist": [], "sholat": []}
                if s_final and s_final != "-" and status_surah == "Lancar 🌟" and s_final not in capaian["surah"]: capaian["surah"].append(s_final)
                if d_final and d_final != "-" and status_doa == "Lancar 🌟" and d_final not in capaian["doa"]: capaian["doa"].append(d_final)
                if h_final and h_final != "-" and status_hadist == "Lancar 🌟" and h_final not in capaian["hadist"]: capaian["hadist"].append(h_final)
                if sh_final and sh_final != "-" and status_sholat == "Lancar 🌟" and sh_final not in capaian["sholat"]: capaian["sholat"].append(sh_final)
                
                # Simpan capaian baru ke Supabase
                supabase.table('santri').update({"capaian": capaian}).eq('username', username_terpilih).execute()
                
                # Merangkai Narasi
                narasi = []
                narasi.append(f"✨ *Assalamu'alaikum Ayah/Bunda!*\n\nAlhamdulillah, hari ini *{nama_panggilan}* ({input_kehadiran}) telah mengikuti kegiatan belajar dengan baik. Berikut progresnya:")
                if input_jilid != "-" and input_hal != "":
                    if input_status_baca == "Lancar": narasi.append(f"📖 *Membaca:* Lancar membaca {input_jilid} Halaman {input_hal}.")
                    else: narasi.append(f"📖 *Membaca:* Mohon bantu murojaah {input_jilid} Hal {input_hal}. *(Fokus perbaikan: {input_huruf_sulit})*")
                
                if s_final and s_final != "-": narasi.append(f"🌟 *Surah:* {s_final} " + ("(Lancar ✅)" if status_surah == "Lancar 🌟" else "(Perlu diulang 🔄)"))
                if d_final and d_final != "-": narasi.append(f"🤲 *Do'a:* {d_final} " + ("(Lancar ✅)" if status_doa == "Lancar 🌟" else "(Perlu diulang 🔄)"))
                if h_final and h_final != "-": narasi.append(f"📜 *Hadist:* {h_final} " + ("(Lancar ✅)" if status_hadist == "Lancar 🌟" else "(Perlu diulang 🔄)"))
                if sh_final and sh_final != "-": narasi.append(f"🕋 *Sholat:* {sh_final} " + ("(Lancar ✅)" if status_sholat == "Lancar 🌟" else "(Perlu diulang 🔄)"))
                    
                if input_fokus != "-" or input_adab != "-": narasi.append(f"🌱 *Sikap Kelas:* Fokus {input_fokus}, Adab {input_adab}.")
                if input_catatan: narasi.append(f"📝 *Catatan:* _{input_catatan}_")
                narasi.append("---\n💡 Mohon klik *✅ Tandai Sudah Murojaah* di Aplikasi Sinergi jika sudah diulang di rumah.")

                laporan_akhir = "\n\n".join(narasi)
                
                # Simpan ke Tabel Laporan Harian di Supabase
                bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                bulan_ini = f"{bulan_indo[datetime.datetime.now().month - 1]} {datetime.datetime.now().year}"
                
                supabase.table('laporan_harian').insert({
                    "username_santri": username_terpilih,
                    "tanggal": datetime.datetime.now().strftime("%d %B %Y"),
                    "bulan_tahun": bulan_ini,
                    "kehadiran": input_kehadiran,
                    "narasi_laporan": laporan_akhir,
                    "status_murojaah": False
                }).execute()
                
                st.success("✅ Laporan harian dan pencapaian kurikulum berhasil disimpan di Database!")
                
                # Menyiapkan tombol WA
                no_hp = user_data.get("no_hp", "")
                if no_hp:
                    if no_hp.startswith('0'): no_hp = '62' + no_hp[1:]
                    pesan_wa = urllib.parse.quote(laporan_akhir)
                    link_wa = f"https://wa.me/{no_hp}?text={pesan_wa}"
                    
                    st.markdown(f"""
                    <a href='{link_wa}' target='_blank' style='text-decoration: none;'>
                        <div style='background-color: #25D366; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold;'>
                            📲 KIRIM LAPORAN KE WHATSAPP ORANG TUA
                        </div>
                    </a>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Tombol WhatsApp tidak muncul karena nomor HP orang tua belum diisi pada form biodata.")

    # --- TAB 2: PROGRES HAFALAN ---
    with tab2:
        st.subheader("📈 Progres Hafalan Kurikulum Kelas")
        pilih_santri_progres = st.selectbox("Lihat Progres Santri:", daftar_nama_anak, key="progres_guru")
        username_progres = map_nama_ke_username[pilih_santri_progres]
        
        user_prog = next((item for item in data_santri_list if item["username"] == username_progres), {})
        capaian_anak = user_prog.get("capaian") or {"surah": [], "doa": [], "hadist": [], "sholat": []}
        
        col_s, col_d = st.columns(2)
        with col_s:
            st.success("**🌟 Surah yang Sudah Lancar:**")
            if capaian_anak.get("surah"): 
                for item in capaian_anak["surah"]: st.write(f"- ✅ {item}")
            else: st.write("- *Belum ada data*")
        with col_d:
            st.success("**🤲 Do'a yang Sudah Lancar:**")
            if capaian_anak.get("doa"): 
                for item in capaian_anak["doa"]: st.write(f"- ✅ {item}")
            else: st.write("- *Belum ada data*")
            
        col_h, col_sh = st.columns(2)
        with col_h:
            st.success("**📜 Hadist yang Sudah Lancar:**")
            if capaian_anak.get("hadist"): 
                for item in capaian_anak["hadist"]: st.write(f"- ✅ {item}")
            else: st.write("- *Belum ada data*")
        with col_sh:
            st.success("**🕋 Sholat yang Sudah Lancar:**")
            if capaian_anak.get("sholat"): 
                for item in capaian_anak["sholat"]: st.write(f"- ✅ {item}")
            else: st.write("- *Belum ada data*")

    # --- TAB 3: BUKU PENGHUBUNG ---
    with tab3:
        pilih_santri_chat = st.selectbox("Pilih Ruang Chat:", daftar_nama_anak, key="chat_guru")
        username_chat = map_nama_ke_username[pilih_santri_chat]
        
        # Tarik data chat dari Supabase
        chat_res = supabase.table('buku_penghubung').select('*').eq('username_santri', username_chat).order('created_at', desc=False).execute()
        for pesan in chat_res.data:
            if pesan["pengirim"] == "Guru": st.success(f"**Anda** ({pesan['waktu_kirim']}):\n\n{pesan['isi_pesan']}")
            else: st.info(f"**Ortu** ({pesan['waktu_kirim']}):\n\n{pesan['isi_pesan']}")
                
        with st.form("form_balas"):
            balasan = st.text_area("Tulis balasan Anda:")
            if st.form_submit_button("Kirim Balasan") and balasan.strip():
                supabase.table('buku_penghubung').insert({
                    "username_santri": username_chat,
                    "pengirim": "Guru",
                    "waktu_kirim": datetime.datetime.now().strftime("%d %B %Y - %H:%M"),
                    "isi_pesan": balasan
                }).execute()
                st.rerun()

    # --- TAB 4: REKAP KEHADIRAN (Dinamic Data Cloud) ---
    with tab4:
        st.subheader(f"📊 Rekapitulasi Kehadiran Kelas {kelas_saya}")
        bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        bulan_ini = f"{bulan_indo[datetime.datetime.now().month - 1]} {datetime.datetime.now().year}"
        st.write(f"Data Periode: **{bulan_ini}**")
        
        data_rekap_kelas = []
        
        # Tarik semua absen bulan ini khusus santri di kelas admin
        absen_res = supabase.table('laporan_harian').select('username_santri, kehadiran').eq('bulan_tahun', bulan_ini).execute()
        semua_absen = absen_res.data
        
        for data in data_santri_list:
            nama = data.get("nama_lengkap") or data.get("nama_panggilan")
            
            # Hitung absensi masing-masing dari hasil Query
            hadir = len([x for x in semua_absen if x['username_santri'] == data['username'] and x['kehadiran'] == 'Hadir'])
            sakit = len([x for x in semua_absen if x['username_santri'] == data['username'] and x['kehadiran'] == 'Sakit'])
            izin = len([x for x in semua_absen if x['username_santri'] == data['username'] and x['kehadiran'] == 'Izin'])
            alpa = len([x for x in semua_absen if x['username_santri'] == data['username'] and x['kehadiran'] == 'Alpa'])
            
            data_rekap_kelas.append({
                "Nama Santri": nama, "Hadir": hadir, "Sakit": sakit, "Izin": izin, "Alpa": alpa
            })
            
        st.dataframe(data_rekap_kelas, use_container_width=True)

    # --- TAB 5: DATA KELAS ---
    with tab5:
        data_tabel = []
        for data in data_santri_list:
            data_tabel.append({
                "Nama Lengkap": data.get("nama_lengkap", "Belum Isi"),
                "Username Login": data["username"],
                "Password": data["password"],
                "No HP": data.get("no_hp", "-")
            })
        st.dataframe(data_tabel, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Keluar (Logout)", type="primary"):
        st.session_state.update({'logged_in': False, 'role': '', 'username': '', 'kelas_admin': ''})
        st.rerun()