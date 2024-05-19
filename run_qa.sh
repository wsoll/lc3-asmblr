echo "Running black..."
black --check src/ test/

echo "Running flake8..."
flake8 src/ test/

echo "Running mypy..."
mypy src/