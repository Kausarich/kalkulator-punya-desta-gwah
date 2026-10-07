# Tindak lanjut audit Desta Calculator

Tanggal: 7 Oktober 2026. Acuan: audit 36 temuan. Status tabel berarti perubahan kode telah diterapkan, bukan seluruh skenario sudah diverifikasi pada browser/perangkat fisik.

| ID | Perbaikan yang diterapkan | Lokasi utama |
| --- | --- | --- |
| 01 | Rumus awal tahun, kabisat dan panjang bulan Hijriah memakai satu siklus yang konsisten | engine.py, assets/engine.js |
| 02 | UTC 0 diperlakukan sebagai nilai valid; input kosong ditolak terpisah | app.py, assets/qibla.js |
| 03 | Jadwal dan countdown memakai timestamp absolut serta zona lokasi | engine.py, assets/engine.js |
| 04 | Cache jadwal diperbarui saat tanggal lokasi berubah; kandidat hari berikutnya disiapkan | app.py, assets/qibla.js |
| 05 | Operasi lanjutan memakai nilai Ans, sehingga kuadrat hasil negatif mempertahankan pengelompokan | calculator.py, assets/calculator.js |
| 06 | Semua pangkat termasuk 10^x melalui batas eksponen dan floating point finite | engine.py, assets/engine.js |
| 07 | Parser angka menerima nol di depan dan input multidigit | engine.py, assets/engine.js |
| 08 | Kontrak floating point dan sisa bagi disamakan; literal melampaui batas aman ditolak | engine.py, assets/engine.js |
| 09 | Fungsi unary diterapkan pada operand terakhir atau kelompok terakhir | calculator.py, assets/calculator.js |
| 10 | Tangen pada singularitas mengembalikan kesalahan domain | engine.py, assets/engine.js |
| 11 | Validasi tanggal sebenarnya, waktu, UTC, dan panjang bulan Hijriah | engine.py, assets/engine.js |
| 12 | Rentang koordinat divalidasi; mengedit input mengganti label menjadi manual dan membatalkan hasil lama | app.py, assets/qibla.js |
| 13 | Waktu sekarang desktop membaca offset sistem | app.py |
| 14 | Isian tanggal web dibuat dari tanggal lokal, tanpa pemotongan ISO UTC | assets/engine.js, assets/calendar.js |
| 15 | Invers JD memakai Gregorian proleptik dan batas tengah malam; tahun 1–99 ditangani eksplisit | engine.py, assets/engine.js |
| 16 | Judul kalender mencantumkan kedua tahun Hijriah ketika rentang melintasi tahun | app.py, assets/calendar.js |
| 17 | Pemilihan tanggal diselaraskan dengan bulan yang ditampilkan | app.py, assets/calendar.js |
| 18 | Event relatif ditolak; heading tanpa koreksi deklinasi dilabeli perkiraan | assets/compass.js, index.html |
| 19 | Satu jalur aktivasi sensor meminta izin; jeda tersedia ketika permintaan masih tertunda | assets/compass.js, assets/qibla.js |
| 20 | Generasi permintaan mencegah callback GPS/izin lama mengaktifkan ulang kompas | assets/compass.js |
| 21 | Heading tak tersedia/kedaluwarsa kembali ke referensi statis dengan status jelas | assets/compass.js |
| 22 | Kompas digerakkan event; tab tersembunyi menjeda sensor; getar hanya saat memasuki kondisi sejajar | assets/app.js, assets/qibla.js |
| 23 | Geometri kompas web memakai proporsi relatif dan SVG viewBox | assets/styles.css, index.html |
| 24 | Semua tab desktop mendapat kontainer gulir; kalkulator reflow, tabel gulir, teks membungkus | widgets.py, app.py |
| 25 | Font tidak lagi ditimpa reset universal; input/hasil memakai monospace | assets/styles.css |
| 26 | CSS terpusat per komponen; style inline statis dan lapisan override lama dihapus | assets/styles.css, index.html |
| 27 | Blur dihapus; reduced motion menonaktifkan transisi dan haptik | assets/styles.css, assets/qibla.js |
| 28 | Deskripsi diringkas, rincian metode dipindah ke disclosure; aktivasi sensor tidak diduplikasi | index.html, app.py |
| 29 | Label pengguna berbahasa Indonesia; daftar kota/bulan/hari/peringatan memakai sumber data bersama | data.json, assets/data.js |
| 30 | Label input, ARIA tab/pressed, fokus keyboard, tanggal bertombol, caption/header tabel | index.html, assets/calendar.js, assets/app.js |
| 31 | Kegagalan input menampilkan pesan; hasil terkait ditandai usang/dibersihkan | app.py, assets/*.js |
| 32 | State sensor, variabel lokal, style dan jalur kode lama yang tidak dipakai dihapus | app.py, assets/*.js, assets/styles.css |
| 33 | Program CLI dipindah ke cli.py; rumusnya menggunakan engine bersama | cli.py |
| 34 | Dokumentasi disesuaikan dengan metode aktual, batas numerik, fitur sensor dan arsitektur | SYSTEM_DOCUMENTATION.md |
| 35 | Bytecode dihapus dari indeks Git; cache dan virtual environment diabaikan | .gitignore |
| 36 | UI, state kalkulator, engine, data dan sensor dipisah; duplikasi rumus pada CLI dihapus | engine.py, calculator.py, widgets.py, assets/ |

## Batas verifikasi

Pemeriksaan sintaks dan tinjauan sumber dilakukan; tidak ada suite regresi baru yang ditambahkan. Verifikasi visual lintas breakpoint/browser, pembaca layar, serta izin GPS dan sensor nyata masih perlu dilakukan. Implementasi web dan Python tetap memakai dua engine bahasa berbeda; keduanya harus dipelihara bersama sesuai kontrak pada dokumentasi.

Perubahan pada tahap ini bersifat lokal dan belum dipush.
