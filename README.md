# Kasir POS — Clean Light Mobile Design (pen.dev)

Desain aplikasi kasir toko retail: 19 screens HP 390×844 + 7 komponen
reusable + 14 design variables. Format `.pen` (schema v2.19, valid).

## Buka desain

1. Install **pen.dev desktop** (https://pen.dev/downloads)
2. Clone repo ini, buka `kasir-pos.pen` (File → Open)
3. Kalau kanvas kosong tekan **Ctrl+0** (zoom to fit)
4. **Jangan pisahkan** `kasir-pos.pen` dari folder `assets/`
   (image fill foto produk pakai path relatif `./assets/`)

## Isi

| File / folder | Keterangan |
|---|---|
| `kasir-pos.pen` | File desain utama (19 screens, 423 nodes) |
| `assets/` | 11 foto produk asli (square 400×400) |
| `preview-html/` | 4 mockup HTML interaktif (klik ganda di Chrome) |
| `gen_full_pen.py` | Generator `.pen` (regenerate: `python3 gen_full_pen.py`) |

## Alur screens

Splash → Login → PIN → Pilih Shift → Katalog → Detail Produk →
Keranjang → Pelanggan → Bayar Tunai → Bayar QRIS → Sukses →
Struk → Riwayat → Detail+Retur → Tutup Shift → Stok →
Tambah Produk → Laporan → Pengaturan

## Update

Tiap ada revisi, file di repo ini ikut terupdate. Di Windows:

```bat
git pull
```

atau pakai GitHub Desktop → Fetch origin.
