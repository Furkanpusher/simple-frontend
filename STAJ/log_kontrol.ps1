while ($true) { 
   $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
   
   # task_log.txt'ye başlangıç bilgisi yaz
   Add-Content -Path "task_log.txt" -Value "[$timestamp] Log analiz döngüsü başladı" -Encoding UTF8
   Write-Host "[$timestamp] Log kontrol ediliyor..."
   
   # hatalar.txt'yi temizle (eski veriler kalmasın)
   Clear-Content -Path "hatalar.txt" -ErrorAction SilentlyContinue
   
   # Docker'dan hataları filtrele burasını genişletebilirim
    docker logs log_analyzer_redis | Select-String -Pattern "ERR|ERROR|FAIL|FATAL|WARNING" | Out-File "hatalar.txt" -Encoding UTF8
   
   # Kaç hata bulunduğunu say
   $hata_sayisi = (Get-Content "hatalar.txt" -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
   
   if ($hata_sayisi -gt 0) {
       # API'ye dosya analizini gönder
       try {
           $api_response = Invoke-RestMethod -Uri "http://localhost:8001/analyze-file" -Method POST
           $task_ids = $api_response.task_ids
           
           Add-Content -Path "task_log.txt" -Value "[$timestamp] $hata_sayisi hata Gemini'ya gönderildi: $($api_response.message)" -Encoding UTF8
           Write-Host "[$timestamp] $hata_sayisi hata AI analizine gonderildi"
           
           # AI analiz sonuçlarının hazır olması için biraz bekle
           Write-Host "[$timestamp] AI analizi bekleniyor (10 saniye)..."-Encoding UTF8
           Start-Sleep 10
           
           # Task sonuçlarını al ve dosyaya yaz
           try {
                $body = @{
                    task_ids = $task_ids
                } | ConvertTo-Json
                
                $results_response = Invoke-RestMethod -Uri "http://localhost:8001/get-all-results" -Method POST -Body $body -ContentType "application/json"
                Add-Content -Path "task_log.txt" -Value "[$timestamp] AI sonucları alındı: $($results_response.message)" -Encoding UTF8
                Write-Host "[$timestamp] AI sonucları analiz_sonuclari.txt'ye yazıldı" -Encoding UTF8
            }
            catch {
                Add-Content -Path "task_log.txt" -Value "[$timestamp] Sonuç alma hatası: $($_.Exception.Message)" -Encoding UTF8
                Write-Host "[$timestamp] Sonuç alma hatası"
            }
       }
       catch {
           Add-Content -Path "task_log.txt" -Value "[$timestamp] API hatası: $($_.Exception.Message)" -Encoding UTF8
           Write-Host "[$timestamp] API hatası oluştu"
       }
   } else {
       Add-Content -Path "task_log.txt" -Value "[$timestamp] Hiç hata bulunamadı" -Encoding UTF8
       Write-Host "[$timestamp] Hic hata bulunamadı"
   }
   
   Write-Host "[$timestamp] 30 saniye bekleniyor..."
   Start-Sleep 30
}

# çalıştırmak için:
# PowerShell -ExecutionPolicy Bypass -File log_kontrol.ps1
