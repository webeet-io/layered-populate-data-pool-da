#!/bin/bash

echo "=== Git Merge Script: Force updating db-population-utils-design ==="

# 1. Убедимся что мы запушили нашу ветку
echo "Ensuring our branch is pushed..."
git push origin db-population-utils-design-svitlana

# 2. Переключимся на основную ветку
echo "Switching to main branch db-population-utils-design..."
git checkout db-population-utils-design

# 3. Принудительно обновляем основную ветку содержимым нашей ветки
echo "Force updating main branch with our changes..."
git reset --hard db-population-utils-design-svitlana

# 4. Принудительно пушим в основную ветку (перезаписываем удаленную ветку)
echo "Force pushing to main branch..."
git push --force-with-lease origin db-population-utils-design

# 5. Показываем результат
echo "Checking final status..."
git log --oneline -5

echo "=== Force merge completed! ==="
echo "Branch db-population-utils-design now matches db-population-utils-design-svitlana"
echo "Main branch db-population-utils-design now contains all your changes"
# 6. Опционально - удаляем нашу рабочую ветку
echo "Optionally delete the feature branch..."
echo "To delete feature branch run: git branch -d db-population-utils-design-svitlana"
echo "To delete remote feature branch run: git push origin --delete db-population-utils-design-svitlana"

echo "=== Merge completed! ==="
