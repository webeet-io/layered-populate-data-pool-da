#!/bin/bash

echo "=== Push to Design Branch Only ==="

# 1. Убедимся что все изменения закоммичены
echo "Committing any uncommitted changes..."
git add .
git commit -m "Final updates before pushing to design branch" || echo "No changes to commit"

# 2. Убедимся что мы на правильной ветке
echo "Current branch:"
current_branch=$(git branch --show-current)
echo "We are on: $current_branch"

# 3. Если мы не на нашей рабочей ветке, переключимся
if [ "$current_branch" != "db-population-utils-design-svitlana" ]; then
    echo "Switching to our working branch..."
    git checkout db-population-utils-design-svitlana
fi

# 4. Пушим нашу рабочую ветку
echo "Pushing our working branch..."
git push --force-with-lease origin db-population-utils-design-svitlana

# 5. Переключаемся на ветку design (НЕ main!)
echo "Switching to db-population-utils-design branch..."
git checkout db-population-utils-design

# 6. Принудительно обновляем design ветку нашими изменениями
echo "Updating design branch with our changes..."
git reset --hard db-population-utils-design-svitlana

# 7. Пушим ТОЛЬКО в design ветку (НЕ в main!)
echo "Pushing to design branch (NOT main)..."
git push --force-with-lease origin db-population-utils-design

# 8. Возвращаемся на нашу рабочую ветку
echo "Returning to our working branch..."
git checkout db-population-utils-design-svitlana

echo "=== SUCCESS! ==="
echo "✅ Changes pushed ONLY to db-population-utils-design branch"
echo "✅ Main branch was NOT touched"
echo "Current branch: $(git branch --show-current)"
