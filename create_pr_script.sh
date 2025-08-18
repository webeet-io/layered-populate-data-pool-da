#!/bin/bash

echo "=== Creating Pull Request (Protected Branch) ==="

# 1. Убедимся что все изменения закоммичены
echo "Committing any uncommitted changes..."
git add .
git commit -m "Final updates before creating PR" || echo "No changes to commit"

# 2. Убедимся что мы на правильной ветке
echo "Current branch:"
current_branch=$(git branch --show-current)
echo "We are on: $current_branch"

# 3. Пушим нашу рабочую ветку (если ещё не запушена)
echo "Pushing our working branch..."
git push origin db-population-utils-design-svitlana

# 4. Ветка db-population-utils-design защищена! Создаём PR вместо force push
echo "Branch db-population-utils-design is PROTECTED!"
echo "Creating Pull Request instead..."

# 5. Проверяем есть ли GitHub CLI
if command -v gh &> /dev/null; then
    echo "Creating PR via GitHub CLI..."
    gh pr create \
      --title "Complete SmartAutoDataLoader Implementation" \
      --body "## SmartAutoDataLoader Enhancement

### Features Added:
- ✅ Smart JSON complexity analysis (504+ columns extraction)
- ✅ Deep flattening for nested JSON structures  
- ✅ Enhanced datetime detection across all formats
- ✅ Comprehensive error handling
- ✅ Fixed import issues in test notebooks
- ✅ Performance optimizations for large files

### Testing Complete:
- CSV tests passing (95% priority - CRITICAL)
- Excel tests passing (80% priority - HIGH)  
- JSON tests passing (70% priority - MEDIUM)
- All edge cases handled

### Ready for Review and Merge into db-population-utils-design" \
      --base db-population-utils-design \
      --head db-population-utils-design-svitlana
else
    echo "GitHub CLI not installed. Please create PR manually:"
    echo ""
    echo "🌐 Go to: https://github.com/webeet-io/layered-populate-data-pool-da"
    echo "📋 Create Pull Request:"
    echo "   From: db-population-utils-design-svitlana"
    echo "   To:   db-population-utils-design"
    echo "   Title: Complete SmartAutoDataLoader Implementation"
    echo ""
    echo "📝 Description to use:"
    echo "## SmartAutoDataLoader Enhancement
    
### Features Added:
- ✅ Smart JSON complexity analysis (504+ columns extraction)
- ✅ Deep flattening for nested JSON structures  
- ✅ Enhanced datetime detection across all formats
- ✅ Comprehensive error handling
- ✅ Performance optimizations for large files

### Ready for Review and Merge"
fi

echo "=== SOLUTION: Pull Request Created/Instructions Provided ==="
echo "✅ Cannot force-push to protected branch - this is GOOD security!"
echo "✅ Pull Request is the proper way to merge into protected branches"
