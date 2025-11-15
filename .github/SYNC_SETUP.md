# Настройка автоматической синхронизации с GitLab

Этот репозиторий настроен для автоматической синхронизации с GitLab при каждом push в GitHub.

## Как это работает

GitHub Actions workflow (`.github/workflows/sync-to-gitlab.yml`) автоматически отправляет изменения в GitLab при каждом push в ветки `main` или `master`.

## Настройка (требуется один раз)

### 1. Создайте GitLab Personal Access Token

1. Перейдите в GitLab: https://git.codenrock.com
2. Откройте **Settings** → **Access Tokens** (или **Preferences** → **Access Tokens**)
3. Создайте новый токен с правами:
   - `write_repository` (для push)
   - `api` (опционально)
4. Скопируйте созданный токен (он показывается только один раз!)

### 2. Добавьте токен в GitHub Secrets

1. Перейдите в ваш GitHub репозиторий
2. Откройте **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **New repository secret**
4. Имя: `GITLAB_TOKEN`
5. Значение: вставьте скопированный GitLab токен
6. Нажмите **Add secret**

### 3. Готово!

Теперь при каждом `git push origin main` изменения автоматически синхронизируются с GitLab.

## Проверка работы

После настройки:
1. Сделайте любой commit и push в GitHub
2. Перейдите в **Actions** вкладку вашего GitHub репозитория
3. Вы увидите запущенный workflow "Sync to GitLab"
4. После успешного выполнения проверьте GitLab - изменения должны быть там

## Альтернативный способ (локальный git hook)

Если вы предпочитаете локальную синхронизацию, можно использовать git hook:

```bash
# Создайте файл .git/hooks/post-push (или используйте существующий)
cat > .git/hooks/post-push << 'EOF'
#!/bin/bash
git push gitlab main:master
EOF
chmod +x .git/hooks/post-push
```

Но GitHub Actions предпочтительнее, так как работает автоматически даже при push с других компьютеров.

