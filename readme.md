# Claude MCP Weather Plugin

## Deskripsi

Plugin ini adalah **MCP Server** (Model Context Protocol) untuk Claude Desktop yang menyediakan dua tool utama:
- **get_current_weather**: Mendapatkan cuaca saat ini untuk kota tertentu.
- **get_weather_forecast**: Mendapatkan prakiraan cuaca 5 hari ke depan untuk kota tertentu.

Plugin ini terhubung ke Claude Desktop melalui protokol MCP dan menggunakan data dari [OpenWeatherMap](https://openweathermap.org/).

---

## Cara Instalasi & Konfigurasi

### 1. **Clone Repo & Install Dependency**
```sh
git clone <repo-anda>
cd mcp_server
pip install -r requirements.txt
```

### 2. **Siapkan API Key OpenWeatherMap**
Dapatkan API key dari https://openweathermap.org/api dan simpan di file `.env`:
```
OWM_API_KEY=isi_api_key_anda
```
Atau, pastikan sudah diatur di environment variable.

### 3. **Konfigurasi Claude Desktop**
Edit atau buat file:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```
Contoh konfigurasi:
```json
{
  "mcpServers": {
    "weather": {
      "command": "/Users/macbook/miniconda3/envs/binar/bin/python",
      "args": ["/Users/macbook/Documents/projects/mcp_server/weather_fixed.py"],
      "cwd": "/Users/macbook/Documents/projects/mcp_server",
      "env": {
        "OWM_API_KEY": "isi_api_key_anda"
      }
    }
  }
}
```

### 4. **Jalankan Claude Desktop**
- Buka Claude Desktop, plugin akan otomatis terdeteksi.
- Pastikan tidak ada error pada log Claude.

---

## Cara Menggunakan

Cukup gunakan prompt natural language di Claude Desktop, misal:
- `Tampilkan cuaca saat ini di Jakarta`
- `Bagaimana prakiraan cuaca 5 hari ke depan untuk Surabaya?`

Claude akan otomatis memanggil tool MCP yang sesuai.

---

## Tool yang Tersedia

### 1. get_current_weather
- **Input:** `city` (string)
- **Output:** Cuaca saat ini (suhu, kondisi, kelembapan, tekanan, kecepatan angin, visibilitas)

### 2. get_weather_forecast
- **Input:** `city` (string)
- **Output:** Prakiraan cuaca 5 hari ke depan (tiap 3 jam, suhu, kondisi, kelembapan)

---

## Troubleshooting

- **API Key Error:**  
  Jika muncul `ERROR: OWM_API_KEY environment variable is not set`, pastikan API key sudah benar di `.env` atau config Claude.
- **Timeout/Server Disconnected:**  
  Pastikan dependensi sudah terinstall, port tidak bentrok, dan tidak ada error pada kode.
- **Claude tidak memanggil tool:**  
  Restart Claude Desktop setelah mengubah config/plugin.

---

## Ringkasan Log Integrasi & Error

### Contoh Log Error & Penyebabnya

- **spawn uv ENOENT / spawn python ENOENT**  
  Penyebab: Python/uv tidak ditemukan di PATH.  
  Solusi: Pastikan environment dan dependensi sudah benar.

- **OWM_API_KEY environment variable is not set**  
  Penyebab: API key tidak di-set.  
  Solusi: Tambahkan API key di `.env` atau config Claude.

- **MCP error -32001: Request timed out**  
  Penyebab: Claude tidak mendapat respon dari MCP server.  
  Solusi: Pastikan server berjalan normal, port benar, dan API key valid.

- **Method not found**  
  Penyebab: Claude memanggil method yang tidak diimplementasikan.  
  Solusi: Abaikan jika tidak butuh, atau implementasikan jika perlu.

### Contoh Log Sukses (Tanpa Error)

```
[info] [weather] Server started and connected successfully
[info] [weather] Message from client: {"method":"initialize", ...}
[info] [weather] Message from server: {"jsonrpc":"2.0","id":1,"result":{"tools":[{"name":"get_current_weather",...},{"name":"get_weather_forecast",...}]}}
[info] [weather] Message from client: {"method":"tools/call","params":{"name":"get_current_weather","arguments":{"city":"Bogor"}}}
[info] [weather] Message from server: {"jsonrpc":"2.0","id":9,"result":{"content":[{"type":"text","text":"Current Weather in Bogor, ID: ..."}],"isError":false}}
[info] [weather] Message from client: {"method":"tools/call","params":{"name":"get_weather_forecast","arguments":{"city":"Salatiga"}}}
[info] [weather] Message from server: {"jsonrpc":"2.0","id":20,"result":{"content":[{"type":"text","text":"5-Day Weather Forecast for Salatiga, ID: ..."}],"isError":false}}
```

---

## Catatan

- Pastikan dependensi Python (`aiohttp`, `python-dotenv`, `mcp-server`, dll) sudah terinstall.
- Untuk debug, cek log Claude Desktop dan log MCP server di terminal.
- Jika ingin menambah tool, cukup tambahkan di file Python dan restart Claude Desktop.

---

## Lisensi

MIT