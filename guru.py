import streamlit as st
import datetime
import urllib.parse
import random  # <-- TAMBAHAN: Untuk memilih motivasi secara acak

def tampilkan_dashboard():
    # Pastikan koneksi dan data sesi tersedia
    if 'supabase' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Silakan login kembali.")
        st.stop()

    supabase = st.session_state['supabase']
    kelas_saya = st.session_state.get('kelas_admin', 'Admin')
    # Ambil ID Lembaga dari sesi login guru
    id_lmbg = st.session_state.get('id_lembaga') 
    kurikulum = st.session_state.get('kurikulum', {})
    
    if not id_lmbg:
        st.error("Gagal mengambil data lembaga. Silakan hubungi Super Admin.")
        st.stop()

    # 1. Ambil info identitas lembaga ini dari database (Dinamis)
    try:
        res_lmbg = supabase.table('info_lembaga').select('*').eq('id_lembaga', id_lmbg).execute()
        if res_lmbg.data:
            info_lb = res_lmbg.data[0]
        else:
            info_lb = {"nama_lembaga": "LEMBAGA TIDAK DIKENAL", "alamat_lembaga": "-"}
            st.error("Data identitas lembaga tidak ditemukan di database.")
    except Exception as e:
        st.error(f"Error mengambil data lembaga: {e}")
        st.stop()
    
    # =========================================================
    # 2. BANNER ELEGAN & MOTIVASI HARIAN PENDIDIK (BARU)
    # =========================================================
    daftar_motivasi_guru = [
        "“Sebaik-baik kalian adalah orang yang belajar Al-Qur'an dan mengajarkannya.” (HR. Bukhari)",
        "“Setiap huruf Al-Qur'an yang dibaca santri akan menjadi amal jariyah yang tak terputus untuk gurunya.”",
        "“Didiklah anak-anak dengan kelembutan, karena kelembutan tidaklah ada pada sesuatu kecuali akan menghiasinya.”",
        "“Kesabaran Ustadz/Ustadzah hari ini adalah pondasi akhlak dan peradaban generasi masa depan.”"
    ]
    motivasi_hari_ini = random.choice(daftar_motivasi_guru)

    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1E7E34 0%, #28A745 100%); padding: 25px; border-radius: 12px; color: white; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size: 14px; opacity: 0.9; margin-bottom: 6px;">🏛️ <b>{info_lb['nama_lembaga']}</b> | 📍 {info_lb['alamat_lembaga']}</div>
        <h2 style="color: white; margin: 0 0 12px 0;">Ahlan wa Sahlan, Ustadz/Ustadzah! 👨‍🏫</h2>
        <p style="font-size: 15px; margin: 0; background-color: rgba(255,255,255,0.18); padding: 12px 16px; border-radius: 8px; font-style: italic;">
            ✨ {motivasi_hari_ini}
        </p>
    </div>
    """, unsafe_allow_html=True)
    # =========================================================
    
    st.title(f"Dasbor Guru - Kelas {kelas_saya}")
    
    # 3. FILTER DATA: Hanya ambil santri di KELAS dan LEMBAGA ini
    res_santri = supabase.table('santri').select('*').eq('kelas', kelas_saya).eq('id_lembaga', id_lmbg).execute()
    data_santri_list = res_santri.data
    
    map_nama_ke_username = {}
    for data in data_santri_list:
        nama_lengkap = data.get("nama_lengkap") or data.get("nama_panggilan", "Santri")
        # Tampilkan tanda tanya jika biodata belum lengkap
        nama_tampil = f"{nama_lengkap} ({data.get('nama_panggilan', '')})" if data.get("biodata_lengkap") else f"❓ {data.get('nama_panggilan', '')}"
        map_nama_ke_username[nama_tampil] = data['username']
            
    daftar_nama_anak = list(map_nama_ke_username.keys())
    
    tab_reward, tab1, tab2, tab3, tab4, tab5, tab_sett = st.tabs([
        "🏆 Papan Reward", 
        "📝 Input Laporan", 
        "📈 Progres Hafalan", 
        "💬 Buku Penghubung", 
        "📅 Kehadiran", 
        "📁 Data Kelas",
        "⚙️ Info Lembaga"
    ])
    
    if not daftar_nama_anak:
        with tab1:
            st.warning(f"Belum ada santri terdaftar di kelas {kelas_saya} pada lembaga {info_lb['nama_lembaga']}.")
        
    # --- TAB REWARD & PENGHARGAAN ---
    with tab_reward:
        st.subheader("🏆 Papan Penghargaan & Prestasi Santri")
        st.caption("Penghargaan dihitung otomatis berdasarkan kehadiran 'Hadir' terbanyak bulan ini dan akumulasi hafalan 'Lancar 🌟'.")
        
        if not data_santri_list:
            st.info("Belum ada data santri untuk kalkulasi reward.")
        else:
            data_reward = []
            # Ambil semua absen untuk lembaga ini
            absen_all = supabase.table('laporan_harian').select('username_santri, kehadiran').execute().data
            
            for santri in data_santri_list:
                nama = santri.get("nama_lengkap") or santri.get("nama_panggilan")
                usr = santri["username"]
                
                # Hitung Total Hafalan Lulus
                capaian = santri.get("capaian") or {"surah": [], "doa": [], "hadist": [], "sholat": []}
                if not isinstance(capaian, dict): capaian = {"surah": [], "doa": [], "hadist": [], "sholat": []}
                
                total_hafalan = len(capaian.get("surah", [])) + len(capaian.get("doa", [])) + \
                                len(capaian.get("hadist", [])) + len(capaian.get("sholat", []))
                
                # Hitung Kehadiran Bulan Ini
                jml_hadir = len([x for x in absen_all if x['username_santri'] == usr and x['kehadiran'] == 'Hadir'])
                
                data_reward.append({
                    "username": usr,
                    "nama": nama,
                    "total_hafalan": total_hafalan,
                    "jml_hadir": jml_hadir,
                    "reward_khusus": santri.get("reward_khusus", "-")
                })
                
            # Urutkan
            terrajin = sorted(data_reward, key=lambda x: x["jml_hadir"], reverse=True)
            terbanyak_hafalan = sorted(data_reward, key=lambda x: x["total_hafalan"], reverse=True)
            
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.success("🌟 **Bintang Hafalan Terbanyak:**")
                if terbanyak_hafalan and terbanyak_hafalan[0]["total_hafalan"] > 0:
                    st.markdown(f"### 🥇 {terbanyak_hafalan[0]['nama']}")
                    st.write(f"**Total Hafalan Lulus:** {terbanyak_hafalan[0]['total_hafalan']} Materi")
                else:
                    st.info("Belum ada pencapaian hafalan yang direkam.")
                    
            with col_r2:
                st.info("🏃 **Santri Paling Rajin Hadir:**")
                if terrajin and terrajin[0]["jml_hadir"] > 0:
                    st.markdown(f"### 🥇 {terrajin[0]['nama']}")
                    st.write(f"**Total Hadir:** {terrajin[0]['jml_hadir']} Kali")
                else:
                    st.info("Belum ada data kehadiran yang direkam.")
                    
            st.markdown("---")
            st.subheader("👑 Nobatkan Penghargaan Khusus / Gelar Akhlak")
            if daftar_nama_anak:
                with st.form("form_nobat_reward"):
                    pilih_santri_reward = st.selectbox("Pilih Santri yang Diberi Penghargaan:", daftar_nama_anak)
                    gelar_input = st.text_input("Gelar Penghargaan / Reward Khusus", placeholder="Cth: 👑 Santri Adab Terbaik Bulan Ini")
                    
                    if st.form_submit_button("Simpan Gelar Penghargaan", use_container_width=True):
                        usr_target = map_nama_ke_username[pilih_santri_reward]
                        try:
                            supabase.table('santri').update({"reward_khusus": gelar_input}).eq('username', usr_target).execute()
                            st.success(f"Berhasil menganugerahkan gelar kepada {pilih_santri_reward}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menyimpan reward: {e}")

    # --- TAB 1: INPUT LAPORAN ---
    with tab1:
        if daftar_nama_anak:
            col_a, col_b = st.columns(2)
            with col_a: pilih_santri_laporan = st.selectbox("1. Pilih Santri untuk Dilaporkan", daftar_nama_anak)
            with col_b: input_jilid = st.selectbox("2. Posisi Bacaan (Buku/Jilid)", ["-", "Iqro 1", "Iqro 2", "Iqro 3", "Iqro 4", "Iqro 5", "Iqro 6", "Al-Qur'an"])
            
            username_terpilih = map_nama_ke_username[pilih_santri_laporan]
            user_data = next((item for item in data_santri_list if item["username"] == username_terpilih), {})
            nama_panggilan = user_data.get('nama_panggilan', 'Ananda')
            
            # Ambil kurikulum sesuai jilid
            materi_tersedia = kurikulum.get(input_jilid, {"sholat": [], "doa": [], "surah": [], "hadist": []})
            opt_surah = ["-"] + materi_tersedia.get("surah", []) + ["Lainnya (Ketik Manual)"]
            opt_doa = ["-"] + materi_tersedia.get("doa", []) + ["Lainnya (Ketik Manual)"]
            opt_sholat = ["-"] + materi_tersedia.get("sholat", []) + ["Lainnya (Ketik Manual)"]
            opt_hadist = ["-"] + materi_tersedia.get("hadist", []) + ["Lainnya (Ketik Manual)"]
            
            with st.form("form_laporan"):
                st.subheader("📍 Kehadiran")
                input_kehadiran = st.radio("Status Kehadiran Hari Ini", ["Hadir", "Sakit", "Izin", "Alpa"], horizontal=True)
                st.markdown("---")
                
                st.subheader("📖 1. Laporan Membaca (Iqro/Al-Qur'an)")
                col1, col2 = st.columns(2)
                with col1: input_hal = st.text_input("Halaman / Ayat", placeholder="Cth: Hal 15 / Ayah 1-5")
                with col2: input_status_baca = st.radio("Evaluasi Membaca", ["Lancar", "Mengulang", "Belum Baca"])
                input_huruf_sulit = st.text_input("Catatan Huruf Sulit / Tajwid (Bila ada)", placeholder="Cth: Masih tertukar di huruf Ja dan Kho")
                st.markdown("---")
                
                st.subheader("🧠 2. Target Kurikulum (Materi Hafalan)")
                st.caption("Pilih materi dan tentukan evaluasinya. Jika 'Lancar 🌟', materi otomatis masuk ke rapor progres permanen.")
                
                c_surah, c_doa = st.columns(2)
                with c_surah:
                    target_surah = st.selectbox("Hafalan Surah Pendek", opt_surah)
                    manual_surah = st.text_input("Ketik Nama Surah (Jika manual)", key="ms")
                    status_surah = st.radio("Evaluasi Surah", ["Lancar 🌟", "Perlu Murojaah", "Belum Setor"], horizontal=True)
                with c_doa:
                    target_doa = st.selectbox("Hafalan Do'a Harian", opt_doa)
                    manual_doa = st.text_input("Ketik Nama Do'a (Jika manual)", key="md")
                    status_doa = st.radio("Evaluasi Do'a", ["Lancar 🌟", "Perlu Murojaah", "Belum Setor"], horizontal=True)
                    
                c_hadist, c_sholat = st.columns(2)
                with c_hadist:
                    target_hadist = st.selectbox("Hafalan Hadist", opt_hadist)
                    manual_hadist = st.text_input("Ketik Nama Hadist (Jika manual)", key="mh")
                    status_hadist = st.radio("Evaluasi Hadist", ["Lancar 🌟", "Perlu Murojaah", "Belum Setor"], horizontal=True)
                with c_sholat:
                    target_sholat = st.selectbox("Bacaan Sholat / Ayat Pilihan", opt_sholat)
                    manual_sholat = st.text_input("Ketik Nama Bacaan (Jika manual)", key="msh")
                    status_sholat = st.radio("Evaluasi Bacaan", ["Lancar 🌟", "Perlu Murojaah", "Belum Setor"], horizontal=True)
                
                st.markdown("---")
                st.subheader("🌱 3. Akhlak, Adab & Catatan")
                col8, col9 = st.columns(2)
                with col8: input_fokus = st.selectbox("Fokus Belajar di Kelas", ["-", "Sangat Baik", "Baik", "Cukup", "Perlu Ditingkatkan"])
                with col9: input_adab = st.selectbox("Adab & Sikap", ["-", "Sangat Baik", "Baik", "Cukup", "Perlu Dibimbing"])
                input_catatan = st.text_area("Pesan Tambahan untuk Orang Tua (Opsional)")
                
                if st.form_submit_button("Simpan & Kirim Laporan Harian", use_container_width=True):
                    # Tentukan nama materi final
                    s_final = manual_surah if target_surah == "Lainnya (Ketik Manual)" else target_surah
                    d_final = manual_doa if target_doa == "Lainnya (Ketik Manual)" else target_doa
                    h_final = manual_hadist if target_hadist == "Lainnya (Ketik Manual)" else target_hadist
                    sh_final = manual_sholat if target_sholat == "Lainnya (Ketik Manual)" else target_sholat
                    
                    # Update Progres Permanen (Jika Lancar)
                    capaian = user_data.get("capaian") or {"surah": [], "doa": [], "hadist": [], "sholat": []}
                    if not isinstance(capaian, dict): capaian = {"surah": [], "doa": [], "hadist": [], "sholat": []}
                    
                    updated_prog = False
                    if s_final and s_final != "-" and status_surah == "Lancar 🌟" and s_final not in capaian["surah"]:
                        capaian["surah"].append(s_final); updated_prog = True
                    if d_final and d_final != "-" and status_doa == "Lancar 🌟" and d_final not in capaian["doa"]:
                        capaian["doa"].append(d_final); updated_prog = True
                    if h_final and h_final != "-" and status_hadist == "Lancar 🌟" and h_final not in capaian["hadist"]:
                        capaian["hadist"].append(h_final); updated_prog = True
                    if sh_final and sh_final != "-" and status_sholat == "Lancar 🌟" and sh_final not in capaian["sholat"]:
                        capaian["sholat"].append(sh_final); updated_prog = True
                    
                    if updated_prog:
                        supabase.table('santri').update({"capaian": capaian}).eq('username', username_terpilih).execute()
                    
                    # Buat Narasi Laporan WhatsApp
                    narasi = []
                    narasi.append(f"✨ *Assalamu'alaikum Ayah/Bunda!*\n\nAlhamdulillah, berikut laporan belajar *{nama_panggilan}* ({input_kehadiran}) hari ini di **{info_lb['nama_lembaga']}**:")
                    
                    if input_kehadiran == "Hadir":
                        if input_jilid != "-" and input_hal != "":
                            if input_status_baca == "Lancar": narasi.append(f"📖 *Membaca:* Lancar di {input_jilid} Halaman {input_hal}. Lanjut!")
                            elif input_status_baca == "Mengulang": narasi.append(f"📖 *Membaca:* Mengulang di {input_jilid} Hal {input_hal}. *(Catatan: {input_huruf_sulit})*")
                        
                        materi_report = []
                        if s_final and s_final != "-" and status_surah != "Belum Setor": materi_report.append(f"- Surah {s_final} ({status_surah})")
                        if d_final and d_final != "-" and status_doa != "Belum Setor": materi_report.append(f"- Do'a {d_final} ({status_doa})")
                        if h_final and h_final != "-" and status_hadist != "Belum Setor": materi_report.append(f"- Hadist {h_final} ({status_hadist})")
                        if sh_final and sh_final != "-" and status_sholat != "Belum Setor": materi_report.append(f"- Bacaan {sh_final} ({status_sholat})")
                        
                        if materi_report:
                            narasi.append(f"🧠 *Materi Hafalan:*\n" + "\n".join(materi_report))
                            
                        if input_fokus != "-" or input_adab != "-":
                            narasi.append(f"🌱 *Sikap:* Fokus kelas {input_fokus}, Adab {input_adab}.")
                            
                    if input_catatan:
                        narasi.append(f"📝 *Catatan Ustadz/ah:* _{input_catatan}_")
                        
                    narasi.append(f"---\n💡 *Pesan Murojaah:* Mohon bantu menyimak ulang hafalan Ananda di rumah nggih Ayah/Bunda.\n📍_{info_lb['alamat_lembaga']}_")

                    laporan_akhir = "\n\n".join(narasi)
                    tgl_ini = datetime.datetime.now().strftime("%d %B %Y")
                    bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
                    bulan_ini_thn = f"{bulan_indo[datetime.datetime.now().month - 1]} {datetime.datetime.now().year}"
                    
                    # Simpan ke Database
                    try:
                        supabase.table('laporan_harian').insert({
                            "username_santri": username_terpilih,
                            "tanggal": tgl_ini,
                            "bulan_tahun": bulan_ini_thn,
                            "kehadiran": input_kehadiran,
                            "narasi_laporan": laporan_akhir,
                            "status_murojaah": False
                        }).execute()
                        
                        st.success("✅ Laporan harian berhasil disimpan di database!")
                        
                        # Tombol Kirim WhatsApp
                        no_hp_ortu = user_data.get("no_hp", "")
                        if no_hp_ortu:
                            if no_hp_ortu.startswith('0'): no_hp_ortu = '62' + no_hp_ortu[1:]
                            pesan_wa_encoded = urllib.parse.quote(laporan_akhir)
                            link_wa = f"https://wa.me/{no_hp_ortu}?text={pesan_wa_encoded}"
                            st.markdown(f"""
                            <a href='{link_wa}' target='_blank' style='text-decoration: none;'>
                                <div style='background-color: #25D366; color: white; padding: 12px; border-radius: 8px; text-align: center; font-weight: bold; margin-top: 10px; font-size: 16px;'>
                                    📲 KLIK DISINI UNTUK KIRIM WA KE ORANG TUA
                                </div>
                            </a>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ No HP Orang Tua belum diisi di biodata, tidak bisa mengirim WA otomatis.")
                            
                    except Exception as e:
                        st.error(f"Gagal menyimpan laporan: {e}")

    # --- TAB 2: PROGRES HAFALAN ---
    with tab2:
        if daftar_nama_anak:
            st.subheader("📈 Progres Hafalan Kurikulum (Materi Berstatus 'Lancar 🌟')")
            pilih_santri_progres = st.selectbox("Lihat Progres Permanen Santri:", daftar_nama_anak, key="progres_guru")
            username_progres = map_nama_ke_username[pilih_santri_progres]
            user_prog = next((item for item in data_santri_list if item["username"] == username_progres), {})
            capaian_anak = user_prog.get("capaian") or {"surah": [], "doa": [], "hadist": [], "sholat": []}
            if not isinstance(capaian_anak, dict): capaian_anak = {"surah": [], "doa": [], "hadist": [], "sholat": []}
            
            col_s, col_d = st.columns(2)
            with col_s:
                st.success("**🌟 Surah yang Sudah Lancar:**")
                if capaian_anak.get("surah"): 
                    for item in capaian_anak["surah"]: st.write(f"- ✅QS. {item}")
                else: st.write("- *Belum ada surah yang disetorkan lancar*")
            with col_d:
                st.success("**🤲 Do'a yang Sudah Lancar:**")
                if capaian_anak.get("doa"): 
                    for item in capaian_anak["doa"]: st.write(f"- ✅ {item}")
                else: st.write("- *Belum ada do'a yang disetorkan lancar*")
                
            col_h, col_sh = st.columns(2)
            with col_h:
                st.success("**📜 Hadist yang Sudah Lancar:**")
                if capaian_anak.get("hadist"): 
                    for item in capaian_anak["hadist"]: st.write(f"- ✅ Hadist {item}")
                else: st.write("- *Belum ada hadist yang disetorkan lancar*")
            with col_sh:
                st.success("**🕋 Bacaan Sholat/Ayat yang Sudah Lancar:**")
                if capaian_anak.get("sholat"): 
                    for item in capaian_anak["sholat"]: st.write(f"- ✅ {item}")
                else: st.write("- *Belum ada bacaan disetorkan lancar*")

    # --- TAB 3: BUKU PENGHUBUNG ---
    with tab3:
        if daftar_nama_anak:
            st.subheader("💬 Buku Penghubung Digital (Ruang Komunikasi)")
            pilih_santri_chat = st.selectbox("Pilih Ruang Chat Santri:", daftar_nama_anak, key="chat_guru")
            username_chat = map_nama_ke_username[pilih_santri_chat]
            
            # Ambil data chat
            chat_res = supabase.table('buku_penghubung').select('*').eq('username_santri', username_chat).order('created_at', desc=False).execute()
            
            # Tampilkan Chat
            st.markdown("---")
            if not chat_res.data:
                st.info("Belum ada riwayat komunikasi. Silakan mulai sapa Orang Tua.")
            else:
                for pesan in chat_res.data:
                    tgl_p = pesan['waktu_kirim']
                    if pesan["pengirim"] == "Guru":
                        st.markdown(f"""
                        <div style="text-align: right; margin-bottom: 10px;">
                            <div style="background-color: #DCF8C6; display: inline-block; padding: 10px; border-radius: 10px; max-width: 80%; text-align: left;">
                                <b>Anda (Guru)</b> <span style="font-size: 10px; color: #888;">{tgl_p}</span><br>
                                {pesan['isi_pesan']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="text-align: left; margin-bottom: 10px;">
                            <div style="background-color: #f1f0f0; display: inline-block; padding: 10px; border-radius: 10px; max-width: 80%;">
                                <b>Orang Tua</b> <span style="font-size: 10px; color: #888;">{tgl_p}</span><br>
                                {pesan['isi_pesan']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
            # Form Kirim Pesan
            with st.form("form_balas_chat", clear_on_submit=True):
                balasan = st.text_area("Tulis pesan baru atau balasan Anda:", placeholder="Tulis disini...")
                if st.form_submit_button("Kirim Pesan", use_container_width=True):
                    if balasan.strip():
                        waktu_ini = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                        try:
                            supabase.table('buku_penghubung').insert({
                                "username_santri": username_chat,
                                "pengirim": "Guru",
                                "waktu_kirim": waktu_ini,
                                "isi_pesan": balasan.strip()
                            }).execute()
                            st.success("Pesan terkirim!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal mengirim pesan: {e}")
                    else:
                        st.warning("Pesan tidak boleh kosong.")

    # --- TAB 4: REKAP KEHADIRAN ---
    with tab4:
        st.subheader(f"📊 Rekapitulasi Kehadiran Kelas {kelas_saya}")
        bulan_indo = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        bulan_ini_thn = f"{bulan_indo[datetime.datetime.now().month - 1]} {datetime.datetime.now().year}"
        st.write(f"Data Periode: **{bulan_ini_thn}**")
        
        # Ambil semua data absen bulan ini untuk kelas & lembaga ini
        try:
            absen_res = supabase.table('laporan_harian').select('username_santri, kehadiran').eq('bulan_tahun', bulan_ini_thn).execute()
            semua_absen = absen_res.data
            
            data_rekap_kelas = []
            for santri in data_santri_list:
                nama = santri.get("nama_lengkap") or santri.get("nama_panggilan")
                hadir = len([x for x in semua_absen if x['username_santri'] == santri['username'] and x['kehadiran'] == 'Hadir'])
                sakit = len([x for x in semua_absen if x['username_santri'] == santri['username'] and x['kehadiran'] == 'Sakit'])
                izin = len([x for x in semua_absen if x['username_santri'] == santri['username'] and x['kehadiran'] == 'Izin'])
                alpa = len([x for x in semua_absen if x['username_santri'] == santri['username'] and x['kehadiran'] == 'Alpa'])
                data_rekap_kelas.append({"Nama Santri": nama, "Hadir 🟢": hadir, "Sakit 🟡": sakit, "Izin 🔵": izin, "Alpa 🔴": alpa})
                
            if data_rekap_kelas:
                st.dataframe(data_rekap_kelas, use_container_width=True)
            else:
                st.info("Belum ada data kehadiran bulan ini.")
        except Exception as e:
            st.error(f"Error memuat rekap kehadiran: {e}")

    # --- TAB 5: DATA KELAS (AKSES LOGIN ORTU) ---
    with tab5:
        st.subheader(f"📁 Daftar Akun Login Orang Tua - Kelas {kelas_saya}")
        st.caption("Gunakan data di bawah ini jika Orang Tua lupa username atau password login mereka.")
        data_tabel = []
        for d in data_santri_list:
            data_tabel.append({
                "Nama Lengkap": d.get("nama_lengkap", "-") or d.get("nama_panggilan"),
                "Username Login": d["username"],
                "Password": d["password"],
                "No HP Ortu": d.get("no_hp", "-")
            })
        
        if data_tabel:
            st.dataframe(data_tabel, use_container_width=True)
        else:
            st.info("Belum ada data santri.")

    # --- TAB 6: PENGATURAN LEMBAGA ---
    with tab_sett:
        st.subheader("⚙️ Pengaturan Identitas Lembaga")
        st.write("Ubah nama dan alamat resmi sekolah/TPQ Anda yang tertera di kop rapor dan narasi WhatsApp:")
        
        with st.form("form_info_lembaga"):
            nama_baru = st.text_input("Nama Lembaga / TPQ / Madrasah", value=info_lb["nama_lembaga"])
            alamat_baru = st.text_area("Alamat Lengkap Lembaga", value=info_lb["alamat_lembaga"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Simpan Perubahan Identitas Lembaga", use_container_width=True):
                if not nama_baru.strip() or not alamat_baru.strip():
                    st.error("Nama dan alamat lembaga tidak boleh kosong.")
                else:
                    try:
                        # Update database
                        supabase.table('info_lembaga').update({
                            "nama_lembaga": nama_baru.strip(),
                            "alamat_lembaga": alamat_baru.strip()
                        }).eq('id_lembaga', id_lmbg).execute()
                        
                        st.success("✅ Identitas lembaga Anda berhasil diperbarui di cloud database!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal memperbarui identitas: {e}")

    # --- LOGOUT BUTTON ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Keluar dari Aplikasi (Logout)", type="primary", use_container_width=True):
        st.session_state.update({'logged_in': False, 'role': '', 'username': '', 'kelas_admin': '', 'id_lembaga': ''})
        st.rerun()