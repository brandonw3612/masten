# if no argument is given, print usage and exit
if [ $# -eq 0 ]; then
    echo "Usage: $0 <grammar-file>"
    exit 1
fi

GRAMMAR_FILE_PATH=$1
GRAMMAR_FILE=$(basename "$GRAMMAR_FILE_PATH")

# The name of the grammar file should be '<lang>-grammar.js'.
# If not, the name is required from the user.
if [[ $GRAMMAR_FILE =~ ^([a-z]+)-grammar\.js$ ]]; then
    LANG_NAME="${BASH_REMATCH[1]}"
    echo "Inferred language name: $LANG_NAME"
else
    echo "The name of the language cannot be inferred from the grammar file name."
    read -p "Please enter the language name (lowercase only): " LANG_NAME
fi

# Ensure the working directory is empty
WORKING_DIR="bpw"
if [ -d "$WORKING_DIR" ]; then
    rm -rf "$WORKING_DIR"
fi
mkdir "$WORKING_DIR"

cd "$WORKING_DIR"
mkdir "tree-sitter-$LANG_NAME"
cd "tree-sitter-$LANG_NAME"

echo "Now we are ready to initilize a parser project."
echo "Please make sure you enter '$LANG_NAME' as the language name when prompted."
tree-sitter init

if [ ! -f "grammar.js" ]; then
    echo "Failed to initialize tree-sitter parser project: grammar.js not found."
    exit 1
fi

cd ../..
echo "Copying grammar file to the parser project..."
cp "$GRAMMAR_FILE_PATH" "$WORKING_DIR/tree-sitter-$LANG_NAME/grammar.js"

cd "$WORKING_DIR/tree-sitter-$LANG_NAME"
echo "Generating parser code..."
tree-sitter generate

echo "Building the parser..."
tree-sitter build

echo "Creating Python bindings..."
python setup.py build_ext --inplace

cd ../..
echo "Copying built parser to the 'parsers' directory..."
if [ ! -d "parsers" ]; then
    mkdir "parsers"
fi
cp -R "$WORKING_DIR/tree-sitter-$LANG_NAME/bindings/python/tree_sitter_$LANG_NAME" "parsers"

echo "Cleaning up..."
rm -rf "$WORKING_DIR"