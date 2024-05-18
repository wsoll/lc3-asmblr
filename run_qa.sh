echo "Running black..."
black --check asmblr/ test/

echo "Running flake8..."
flake8 asmblr/ test/

echo "Running mypy..."
mypy asmblr/