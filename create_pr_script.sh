#!/bin/bash

echo "=== Creating Pull Request via GitHub CLI ==="

# Проверяем, установлен ли GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI (gh) не установлен"
    echo "Установите его: brew install gh"
    echo "Или создайте PR вручную на GitHub.com"
    exit 1
fi

# 1. Аутентификация (если нужно)
echo "Checking GitHub authentication..."
gh auth status || gh auth login

# 2. Создаем Pull Request
echo "Creating Pull Request..."
gh pr create \
  --title "Complete SmartAutoDataLoader Implementation" \
  --body "## SmartAutoDataLoader Enhancement

### Features Added:
- ✅ Smart JSON complexity analysis
- ✅ Deep flattening for nested JSON structures  
- ✅ Enhanced datetime detection across all formats
- ✅ Comprehensive error handling
- ✅ Fixed import issues in test notebooks
- ✅ Performance optimizations for large files

### Testing:
- All CSV tests passing (95% priority - CRITICAL)
- All Excel tests passing (80% priority - HIGH)  
- All JSON tests passing (70% priority - MEDIUM)
- Smart auto-flattening working with 500+ columns extraction

### Ready for Review and Merge" \
  --base db-population-utils-design \
  --head db-population-utils-design-svitlana

echo "=== Pull Request created! ==="
