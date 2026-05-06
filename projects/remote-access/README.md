# Remote Access Toolkit

## Цель
Диагностика и оптимизация удалённых Linux ноутбуков через SSH туннели.

## Способы подключения

### 1. Reverse SSH (основной)
```bash
# На ноутбуке
ssh -R 0.0.0.0:2222:localhost:22 user@server

# На сервере
ssh -p 2222 laptop-user@localhost
```

### 2. ngrok (резервный)
```bash
# На ноутбуке
ngrok tcp 22
# Получишь: tcp://0.tcp.ngrok.io:XXXXX
```

### 3. Tailscale (альтернатива)
```bash
# На ноутбуке и сервере
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
# Используй имя хоста
```

## Быстрая диагностика
```bash
htop          # Процессы
df -h         # Диск
free -h       # ОЗУ
sensors       # Температура
sudo smartctl -a /dev/sda  # SMART
```