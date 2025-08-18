#!/bin/bash

echo "=== Git Push Script for db-population-utils-design-svitlana ==="

# 1. Убедитесь что вы на правильной ветке
echo "Switching to branch db-population-utils-design-svitlana..."
git checkout db-population-utils-design-svitlana

# 2. Добавьте все изменения
echo "Adding all changes..."
git add .

# 3. Сделайте коммит с описанием изменений
echo "Creating commit..."
git commit -m "Complete SmartAutoDataLoader with intelligent JSON processing

- Added smart JSON complexity analysis
- Implemented deep flattening for nested structures  
- Enhanced datetime detection across all formats
- Added comprehensive error handling
- Fixed import issues in test notebooks
- Performance optimizations for large files"

# 4. Принудительный пуш
echo "Force pushing to origin..."
git push --force-with-lease origin db-population-utils-design-svitlana

echo "=== Push completed! ==="
