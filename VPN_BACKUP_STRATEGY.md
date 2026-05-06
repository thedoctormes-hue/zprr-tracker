# VPN Backup Strategy

## Сервера
- **Warsaw**: 185.138.90.150 (REALITY)
- **Florida**: 104.253.1.210 (REALITY)

## Backup план

### 1. Автоматический бэкап ключей
```bash
# Ежедневно в 02:00
0 2 * * * /root/LabDoctorM/scripts/vpn_backup.sh
```

### 2. Хранилище
- **Основное**: шифрованный архив в `/root/.vault/vpn_keys.enc`
- **Резерв**: зашифрованный GitHub gist (ключи только)

### 3. Ротация ключей
- **REALITY**: раз в 90 дней
- **UUID**: раз в 180 дней

### 4. Восстановление
- Сценарий: `ssh root@backup-server "cat /root/.vault/vpn_keys.gpg" | gpg --decrypt`