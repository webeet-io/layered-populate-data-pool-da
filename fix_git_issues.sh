#!/bin/bash

echo "=== Fixing Git Issues ==="

# 1. Сначала закоммитим все незакоммиченные изменения
echo "Committing any uncommitted changes..."
git add .
git commit -m "Add git scripts and fix remaining issues"

# 2. Убедимся что мы на правильной ветке
echo "Current branch:"
git branch --show-current

# 3. Проверим какие ветки существуют
echo "Available branches:"
git branch -a

# 4. Пушим нашу текущую ветку (исправляем название)
echo "Pushing current branch..."
current_branch=$(git branch --show-current)
git push --force-with-lease origin $current_branch

# 5. Если нужно, создадим правильную ветку db-population-utils-design
echo "Creating/updating main design branch..."
git checkout -b db-population-utils-design 2>/dev/null || git checkout db-population-utils-design

# 6. Мерджим наши изменения в основную ветку
echo "Merging changes to main design branch..."
git merge $current_branch --allow-unrelated-histories

# 7. Пушим основную ветку
echo "Pushing main design branch..."
git push -u origin db-population-utils-design

echo "=== Issues fixed! ==="
echo "Current status:"
git status
echo "Available branches:"
git branch -a
