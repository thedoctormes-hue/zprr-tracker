# Security Audit Report — LabDoctorM

**Date:** 2026-05-06
**Auditor:** КотОлизатОр (Qwen Code)

---

## 🔴 CRITICAL FINDINGS

### 1. Token Leaks in Git History
**Status:** Open ⏳
**File:** `AUDIT_2026.md`
**Risk:** MEDIUM — Tokens from legacy `/root/bots` project committed to git (токены НЕ активны, под контролем)

**Exposed Credentials:**
| Type | Token | Status |
|------|-------|--------|
| Telegram Bot | `8616446490:AAEaSLYw...` | Legacy (deactivated, under control) |
| OpenRouter API | `sk-or-v1-3a4de361...` | Legacy (deactivated, under control) |
| Telegram Bot | `8546968865:AAGRp4pD...` | Legacy (deactivated, under control) |
| OpenRouter API | `sk-or-v1-cc672f58...` | Legacy (deactivated, under control) |
| Telegram Bot | `8735680899:AAFOQfjfs...` | Legacy (deactivated, under control) |

**Remediation:** Использовать BFG Repo-Cleaner для очистки git history

### 2. Token in Documentation
**Status:** Fixed ✅
**Files:** `TRANSITION.md`, `QWEN.md` (protocol)
**Issue:** Real `BOT_TOKEN` of Protocolstandbot exposed in markdown

**Fix:** Replaced with placeholder `YOUR_BOT_TOKEN_HERE`

---

## 🟡 MEDIUM FINDINGS

### 3. Duplicate Directories
**Status:** Fixed ✅
**Files:** `.qwen_ant`, `.lab`
**Action:** Removed after verification they were not used

---

## 🟢 GOOD PRACTICES

### 4. .gitignore Properly Configured
- ✅ `.env` и `*.env` в исключениях
- ✅ `tokens.env` в исключениях
- ✅ `MEMORY.md` в исключениях

### 5. Current .env Files Use Placeholders
- Telegram-боты используют реальные токены только в `.env` файлов
- `.env` игнорируются git

---

## 📊 SUMMARY

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 1 | Open (git history) |
| Medium | 1 | Fixed |
| Low | 0 | — |

---

## 🚨 IMMEDIATE ACTIONS REQUIRED

1. **REVOKED:** Все legacy токены больше не активны (подтвердить)
2. **BFG CLEAN:** Запустить `bfg --delete-files AUDIT_2026.md` для очистки git
3. **RE-GIT:** `git reflog expire --expire=now --all && git gc --prune=now --aggressive`

---

## 🔗 References

- Инциденты: `/root/LabDoctorM/INCIDENTS.md`
- Документация: `/root/LabDoctorM/security-report.md`