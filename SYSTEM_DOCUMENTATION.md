# Desta Calculator

Aplikasi web statis dan desktop Python/Tkinter dengan empat modul: kalkulator saintifik, Hari Julian, kiblat/jadwal shalat, serta kalender Masehi/Hijriah.

## Menjalankan

### Desktop (Python 3.10+ dengan Tkinter)

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

`tzdata` menyediakan basis zona waktu IANA, khususnya pada Windows. Tidak ada backend atau akun pengguna.

### Web

Buka `index.html` bersama folder `assets` pada browser modern. Semua font, data, dan perhitungan tersedia lokal. Untuk GPS/sensor pada perangkat seluler, layani melalui HTTPS (atau localhost untuk pengembangan); dukungan dan izin tergantung browser/perangkat.

```powershell
python -m http.server 8000
```

Buka `http://localhost:8000`. Kompas sensor hanya tersedia pada versi web; desktop menampilkan arah statis.

### CLI

```powershell
python cli.py calc "sin(90)+2**3" --mode DEG
python cli.py jd 2026-10-07 --time 12:00:00 --utc 8
python cli.py qibla -6.2088 106.8456
```

CLI berada di `cli.py`; berkas `test.py` lama adalah program interaktif, bukan suite pengujian.

## Kontrak perhitungan

- Mode sudut DEG, RAD, GRAD; default DEG. Digit berurutan membentuk satu bilangan. Nol di depan diterima.
- Pangkat mendahului tanda minus: `-2**2` = −4, `(-2)**2` = 4. Tombol fungsi diterapkan pada operand terakhir; setelah hasil, fungsi memakai `Ans` dengan nilai penuh.
- `%` adalah sisa bagi dengan tanda mengikuti pembilang, konsisten antara Python dan JavaScript.
- Angka menggunakan floating point IEEE-754, sekitar 15 digit signifikan. Bukan aritmetika presisi tak terbatas. Literal biasa di atas 9007199254740991 ditolak; notasi eksponen tetap merupakan pendekatan floating point.
- Ekspresi maksimum 256 karakter, kedalaman 64, nilai absolut eksponen maksimum 10000, faktorial hanya bilangan bulat 0–170. Hasil non-finite dan domain tidak valid menghasilkan pesan kesalahan.
- Hasil besar (≥10^10) atau kecil (<10^-7) ditampilkan sebagai `a × 10^n`; pembulatan tampilan tidak mengganti nilai `Ans`.
- Hari Julian memakai Gregorian proleptik tahun 1–9999. Jam 0–23, menit/detik 0–59, offset UTC −12 hingga +14 termasuk pecahan.
- Hijriah memakai kalender aritmetika siklus 30 tahun, epoch JD 1948439.5. Ini bukan hasil rukyat atau kalender resmi. Tampilan kalender gabungan dibatasi 623–9998 M; konversi Hijriah memvalidasi panjang bulan dan batas hasil Gregorian.
- Preset kota memakai zona IANA, termasuk DST. Koordinat manual/GPS memakai offset yang dapat diedit; zona GPS tidak ditebak dari koordinat. Tanggal jadwal dan countdown mengikuti lokasi, diperbarui ketika tanggal lokasi berganti.
- Shalat merupakan estimasi astronomis: Subuh −20°, Isya −18°, Ashar bayangan satu kali, Imsak 10 menit sebelum Subuh, tambahan 2 menit hanya Dzuhur/Maghrib. Bukan jadwal resmi Kemenag. Fenomena yang tidak terjadi di lintang tinggi ditandai tidak tersedia.
- Arah kiblat statis diukur dari utara sejati. Heading sensor web tidak dikoreksi deklinasi; panduan live berupa perkiraan. Event orientasi relatif ditolak. Pembacaan kedaluwarsa kembali ke arah statis. Permintaan tertunda dibatalkan secara logis ketika kompas dijeda atau tab berubah.

## Struktur

| Berkas | Tanggung jawab |
| --- | --- |
| `engine.py` | Parser matematika, kalender, kiblat, jadwal dan zona waktu |
| `calculator.py` | State interaksi kalkulator desktop |
| `app.py` | Tampilan dan pengikatan event Tkinter |
| `widgets.py` | Tema dan kontainer desktop yang dapat digulir |
| `cli.py` | CLI yang memakai engine Python |
| `index.html` | Struktur semantik UI web |
| `assets/styles.css` | Token tema dan layout responsif web |
| `assets/engine.js` | Engine browser dengan kontrak sama seperti Python |
| `assets/calculator.js`, `calendar.js`, `qibla.js` | Controller tiap modul web |
| `assets/compass.js` | Siklus izin, GPS, pembacaan dan penghentian sensor |
| `assets/app.js` | Navigasi tab dan pengikatan Hari Julian |
| `data.json` | Sumber data kota, bulan, hari dan peringatan kalender |
| `scripts/build_data.py` | Menghasilkan `assets/data.js` untuk browser/file lokal |

Setelah mengubah `data.json`, jalankan `python scripts/build_data.py` dan sertakan hasil `assets/data.js`. Rumus Python dan JavaScript merupakan implementasi terpisah dengan kontrak yang sama; perubahan rumus perlu diterapkan pada keduanya.

## Tampilan dan aksesibilitas

Tema mengikuti referensi neo-brutalist: paper beige, teal, magenta, kuning, border hitam, sudut persegi dan bayangan tegas. Font sistem tidak membutuhkan koneksi jaringan. Web memakai tab dengan navigasi panah/Home/End, label input, tombol tanggal dengan keyboard, fokus terlihat, tabel yang dapat digulir, serta preferensi reduced motion. Desktop menggunakan halaman bergulir dan kalkulator yang berpindah susunan pada lebar sempit (minimum jendela 620×480).

## Status pemeriksaan

Daftar perubahan terhadap audit disimpan dalam `AUDIT_FIXES.md`. Pemeriksaan sumber/sintaks tidak setara dengan verifikasi visual browser, pembaca layar, perangkat GPS, atau sensor kompas fisik. Pemeriksaan perangkat tersebut masih diperlukan sebelum menyatakan kompatibilitas penuh.
