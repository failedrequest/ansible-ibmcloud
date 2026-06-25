#!/usr/bin/env python3
"""
Generate HTML version of README.md using the HTML theme template.
"""

import re
from pathlib import Path


def markdown_to_html(markdown_text):
    """Convert markdown to HTML with basic formatting."""
    html = markdown_text
    
    # Convert headers
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Convert code blocks
    html = re.sub(r'```(\w+)?\n(.*?)```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    
    # Convert inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Convert bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Convert links
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
    
    # Convert unordered lists
    lines = html.split('\n')
    in_list = False
    result = []
    
    for line in lines:
        if line.strip().startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            item = line.strip()[2:]
            result.append(f'<li>{item}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            result.append(line)
    
    if in_list:
        result.append('</ul>')
    
    html = '\n'.join(result)
    
    # Convert paragraphs (lines that aren't already HTML tags)
    lines = html.split('\n')
    result = []
    in_paragraph = False
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append('')
        elif stripped.startswith('<') or stripped.startswith('|'):
            if in_paragraph:
                result.append('</p>')
                in_paragraph = False
            result.append(line)
        else:
            if not in_paragraph:
                result.append('<p>')
                in_paragraph = True
            result.append(line)
    
    if in_paragraph:
        result.append('</p>')
    
    html = '\n'.join(result)
    
    # Convert tables
    html = convert_tables(html)
    
    # Convert checkmarks and badges
    html = html.replace('✅', '<span style="color: #27ae60;">✅</span>')
    html = html.replace('❤️', '<span style="color: #e74c3c;">❤️</span>')
    
    return html


def convert_tables(html):
    """Convert markdown tables to HTML tables."""
    lines = html.split('\n')
    result = []
    in_table = False
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Check if this is a table row
        if line.startswith('|') and line.endswith('|'):
            if not in_table:
                result.append('<table>')
                in_table = True
            
            # Check if next line is separator
            is_header = False
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('|') and '-' in next_line:
                    is_header = True
            
            # Parse cells
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            
            if is_header:
                result.append('<tr>')
                for cell in cells:
                    result.append(f'<th>{cell}</th>')
                result.append('</tr>')
                i += 2  # Skip separator line
                continue
            else:
                result.append('<tr>')
                for cell in cells:
                    result.append(f'<td>{cell}</td>')
                result.append('</tr>')
        else:
            if in_table:
                result.append('</table>')
                in_table = False
            result.append(line)
        
        i += 1
    
    if in_table:
        result.append('</table>')
    
    return '\n'.join(result)


def main():
    """Generate HTML version of README.md."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Read README.md
    readme_path = project_root / "README.md"
    readme_content = readme_path.read_text()
    
    # Read HTML template
    template_path = project_root / "html-theme-template.html"
    template = template_path.read_text()
    
    # Convert markdown to HTML
    html_content = markdown_to_html(readme_content)
    
    # Add navigation menu
    nav_menu = '''
<div class="nav-menu">
    <a href="index.html">Home</a>
    <a href="README.html">README</a>
    <a href="vpc-modules.html">VPC Modules</a>
    <a href="transit-gateway-modules.html">Transit Gateway</a>
    <a href="platform-modules.html">Platform Services</a>
</div>
'''
    
    html_content = nav_menu + html_content
    
    # Replace template placeholders
    html_output = template.replace('{{TITLE}}', 'IBM Cloud Ansible Collection - README')
    html_output = html_output.replace('{{CONTENT}}', html_content)
    
    # Write output
    output_path = project_root / "docs" / "html" / "README.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_output)
    
    print("=" * 60)
    print("README HTML Generator")
    print("=" * 60)
    print(f"\n✓ Generated: {output_path}")
    print(f"\nOpen {output_path} in your browser to view.")
    print("=" * 60)


if __name__ == '__main__':
    main()
