git init
git add .
git commit -m "SH File PUSH" --quiet
git branch -M main

if git remote get-url origin > /dev/null 2>&1; then
    echo "Remote 'origin' already exists, skipping..."
else
    git remote add origin https://github.com/ProjectCuboid/ivyc.git
fi

git push -u origin main --quiet
