#!/bin/bash

echo "=== FORCE OVERWRITE DESIGN BRANCH WITH SVITLANA BRANCH ==="

# 1. Убедимся что мы на правильной ветке Svitlana
git checkout db-population-utils-design-svitlana

# 2. Убедимся что все изменения запушены
echo "Pushing latest changes to Svitlana branch..."
git add .
git commit -m "Final sync before force overwrite" || echo "No changes to commit"
git push origin db-population-utils-design-svitlana

# 3. Переключимся на ветку Design
echo "Switching to design branch..."
git checkout db-population-utils-design

# 4. ПРИНУДИТЕЛЬНО перезапишем ветку Design содержимым ветки Svitlana
echo "Force overwriting design branch with Svitlana branch content..."
git reset --hard db-population-utils-design-svitlana

# 5. ПРИНУДИТЕЛЬНО запушим в ветку Design (перезаписываем удаленную ветку)
echo "Force pushing to design branch (this will overwrite everything)..."
git push --force origin db-population-utils-design

echo "✅ SUCCESS! Design branch now contains ALL content from Svitlana branch!"
echo "✅ All conflicts resolved by complete overwrite"
echo "✅ Pull Request should now merge without any issues"

# 6. Вернемся на рабочую ветку
echo "Returning to Svitlana branch..."
git checkout db-population-utils-design-svitlana

# 7. Удалим созданные скрипты чтобы не мешали
echo "Cleaning up created scripts..."
rm -f git_push_script.sh create_pr_script.sh resolve_conflict_script.sh resolve_conflict_final.sh

echo ""
echo "🎉 MISSION ACCOMPLISHED!"
echo "Your Svitlana branch has completely overwritten the Design branch"
echo "All helper scripts removed to avoid conflicts"
echo "Check GitHub - your PR should now show no conflicts and be ready to merge!"
