#!/bin/bash

echo "=== Finding and Resolving Git Conflicts ==="

# 1. Найдем правильный путь к конфликтному файлу
echo "Searching for the conflicted notebook file..."
find . -name "learn_smart_data_loader.ipynb" -type f

echo "All .ipynb files in project:"
find . -name "*.ipynb" -type f

# 2. Проверим статус git для поиска конфликтов
echo "Git status:"
git status

# 3. Покажем все конфликтные файлы
echo "Checking for actual conflicts:"
git ls-files -u

# 4. Если конфликтов нет, возможно они уже разрешены или нет merge в процессе
if [ -z "$(git ls-files -u)" ]; then
    echo "No conflicts found. Checking if we need to create PR..."
    
    # Добавим все untracked файлы
    echo "Adding untracked files..."
    git add .
    git commit -m "Add helper scripts and resolve any remaining issues"
    
    # Пушим обновления
    echo "Pushing updates..."
    git push origin db-population-utils-design-svitlana
    
    echo "Branch is ready for PR creation!"
else
    echo "Found conflicts, resolving..."
    # Разрешаем все конфликты в пользу нашей версии
    git ls-files -u | cut -f 2 | sort -u | xargs git checkout --ours
    git add .
    git commit -m "Resolve all conflicts in favor of our changes"
    git push origin db-population-utils-design-svitlana
fi

echo "=== Ready to Create Pull Request ==="
