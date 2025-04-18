import os
import ast
import html
import argparse
import re

# Helper to extract class/function doc and structure
def extract_python_info(filepath, base_package):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)
    items = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                'type': 'class',
                'name': node.name,
                'doc': ast.get_docstring(node),
                'methods': [],
                'variables': [],
                'import_path': f"wpilib.{node.name}"
            }
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    method_doc = ast.get_docstring(child)
                    param_docs, return_doc, cleaned_doc = parse_docstring(method_doc or '')
                    class_info['methods'].append({
                        'name': child.name,
                        'doc': cleaned_doc,
                        'param_docs': param_docs,
                        'return_doc': return_doc,
                        'args': [arg.arg for arg in child.args.args]
                    })
                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            class_info['variables'].append(target.id)
            items.append(class_info)
        elif isinstance(node, ast.FunctionDef):
            if(not node.name.startswith("_")):
                items.append({
                    'type': 'function',
                    'name': node.name,
                    'doc': ast.get_docstring(node)
                })

    return items

def parse_docstring(doc):
    param_docs = {}
    return_doc = None
    lines = doc.splitlines()
    cleaned_lines = []

    for line in lines:
        param_match = re.match(r"\s*:param (\w+):\s*(.*)", line)
        if param_match:
            param_docs[param_match.group(1)] = param_match.group(2)
            continue  # skip adding to cleaned_lines

        return_match = re.match(r"\s*:returns?:\s*(.*)", line)
        if return_match:
            return_doc = return_match.group(1)
            continue  # skip adding to cleaned_lines

        cleaned_lines.append(line)

    cleaned_doc = "\n".join(cleaned_lines).strip()
    return param_docs, return_doc, cleaned_doc

# Find all .py files in folder
def find_python_files(folder):
    py_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

# Generate HTML content
def generate_html(doc_data):
    html_parts = ["""
    <html>
    <head>
        <title>Python Class Documentation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 2em;
                background: #f5f5f5;
            }
            .file {
                margin-bottom: 3em;
            }
            h1, h2, h3 {
                font-family: Georgia, serif;
            }
            h2 {
                border-bottom: 1px solid #ccc;
                padding-bottom: 0.25em;
            }
            .class, .function {
                margin: 3em 0;
                padding: 1em;
                background: #ffffff;
                border-left: 5px solid #007acc;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            details {
                margin-top: 1em;
                margin-left: 1em;
                background: #fafafa;
                padding: 1em;
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            .doc {
                color: #444;
                font-style: italic;
                margin-top: 0.5em;
            }
            code {
                font-family: monospace;
                background: #eee;
                padding: 0.2em 0.4em;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <h1>MiniBot API Documentation</h1>
    """]

    for _, items in doc_data.items():
        for item in items:
            if item['type'] == 'class':
                html_parts.append(f'<div class="class"><h2><code>{item["name"]}</code></h2>')
                html_parts.append(f'<div><strong>Import:</strong> <code>import {item["import_path"]}</code></div>')
                if item['doc']:
                    html_parts.append(f'<div class="doc">{html.escape(item["doc"])}</div>')
                html_parts.append('<details><summary>Details</summary>')
                for var in item['variables']:
                    html_parts.append(f'<div>Class Variable: <code>{html.escape(var)}</code></div>')
                for method in item['methods']:
                    html_parts.append('<hr>')
                    method_label = 'Constructor' if method['name'] == '__init__' else 'Method'
                    arglist = ', '.join(method['args'])
                    html_parts.append(f'<div style="margin-top: 1em;"><strong>{method_label}:</strong> <code>{method["name"]}({arglist})</code>')
                    if method['doc']:
                        html_parts.append(f'<div class="doc">{html.escape(method["doc"])}</div>')
                    if method['args']:
                        if(len(method['args']) > 1):
                            html_parts.append('<div><strong>Parameters:</strong><ul>')
                            for arg in method['args']:
                                doc = method['param_docs'].get(arg, '')
                                if(arg != "self"):
                                    html_parts.append(f'<li><code>{arg}</code>: {html.escape(doc)}</li>')
                            html_parts.append('</ul></div>')
                    if method['return_doc']:
                        html_parts.append(f'<div><strong>Returns:</strong> {html.escape(method["return_doc"])}</div>')
                    html_parts.append('</div>')
                html_parts.append('</details></div>')
            elif item['type'] == 'function':
                html_parts.append(f'<div class="function"><strong>Function:</strong> <code>{item["name"]}</code>')
                if item['doc']:
                    html_parts.append(f'<div class="doc">{html.escape(item["doc"])}</div>')
                html_parts.append('</div>')

    html_parts.append("</body></html>")
    return '\n'.join(html_parts)

# Main script
def main():
    parser = argparse.ArgumentParser(description="Generate HTML documentation from Python source files.")
    parser.add_argument('--folder', type=str, default='../wpilib', help='Source folder to scan for Python files')
    parser.add_argument('--output', type=str, default='../www/docs.html', help='Output HTML file path')
    args = parser.parse_args()

    folder = args.folder
    output_file = args.output
    base_package = os.path.basename(folder)
    py_files = find_python_files(folder)
    doc_data = {}
    for py_file in py_files:
        info = extract_python_info(py_file, base_package)
        doc_data[py_file] = info

    html_doc = generate_html(doc_data)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_doc)
        print(f"Documentation written to {output_file}")
    except Exception as e:
        print(f"Failed to write documentation: {e}")

if __name__ == '__main__':
    main()