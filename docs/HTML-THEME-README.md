# HTML Theme Template - Usage Guide

## Overview

This HTML theme provides a professional, clean, and responsive design for converting Markdown documents to HTML. The theme uses web-safe colors and a flat design aesthetic.

## Files

- **html-theme-template.html** - The reusable HTML/CSS template
- **VXLAN-BRIDGE-REMOVAL-PLAN.html** - Example implementation

## Color Scheme

The theme uses a carefully selected color palette:

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Primary Blue | #3498db | Headers, links, info boxes |
| Success Green | #27ae60 | Success messages, recommended badges |
| Warning Orange | #f39c12 | Warnings, fallback badges |
| Danger Red | #e74c3c | Errors, deletion notices, rejected badges |
| Info Teal | #16a085 | H3 headings, informational elements |
| Dark Blue-Gray | #2c3e50 | Body text, code blocks background |
| Light Gray | #ecf0f1 | Page background, code text |
| Medium Gray | #bdc3c7 | Borders, dividers |
| Muted Gray | #95a5a6 | Checklist bullets, blockquotes |

## How to Use

### Method 1: Template Placeholders

The template includes two placeholders:
- `{{TITLE}}` - Replace with your document title
- `{{CONTENT}}` - Replace with your HTML content

**Example:**
```bash
# Read the template
template=$(cat html-theme-template.html)

# Replace placeholders
echo "$template" | \
  sed "s/{{TITLE}}/My Document Title/" | \
  sed "s/{{CONTENT}}/$(cat my-content.html)/" > output.html
```

### Method 2: Manual Integration

1. Copy the `<style>` section from `html-theme-template.html`
2. Paste it into your HTML document's `<head>` section
3. Wrap your content in `<div class="container">...</div>`

### Method 3: External Stylesheet

Extract the CSS to a separate file:

```bash
# Extract CSS from template
sed -n '/<style>/,/<\/style>/p' html-theme-template.html | \
  sed '1d;$d' > theme.css
```

Then link it in your HTML:
```html
<link rel="stylesheet" href="theme.css">
```

## Available CSS Classes

### Box Styles

```html
<div class="info-box">
  Information content with blue left border
</div>

<div class="warning-box">
  Warning content with orange left border
</div>

<div class="success-box">
  Success content with green left border
</div>

<div class="danger-box">
  Danger/error content with red left border
</div>
```

### Badges

```html
<span class="badge badge-recommended">RECOMMENDED</span>
<span class="badge badge-fallback">FALLBACK</span>
<span class="badge badge-rejected">REJECTED</span>
<span class="badge badge-info">INFO</span>
<span class="badge badge-warning">WARNING</span>
<span class="badge badge-success">SUCCESS</span>
<span class="badge badge-danger">DANGER</span>
```

### Architecture Flow Diagrams

```html
<div class="architecture-flow">
Component A
  → Component B
    → Component C
</div>
```

### Checklists

```html
<ul class="checklist">
  <li>Unchecked item 1</li>
  <li>Unchecked item 2</li>
  <li>Unchecked item 3</li>
</ul>
```

### Section Dividers

```html
<div class="section-divider"></div>
```

## Typography

### Headings

- **H1**: Main document title (2.5em, blue underline)
- **H2**: Major sections (1.8em, gray underline)
- **H3**: Subsections (1.4em, teal)
- **H4**: Minor sections (1.2em, green)

### Code

- **Inline code**: `<code>inline code</code>` (light gray background, red text)
- **Code blocks**: `<pre><code>code block</code></pre>` (dark background, light text)

### Text Formatting

- **Bold**: `<strong>important text</strong>`
- **Links**: `<a href="url">link text</a>` (blue, underline on hover)
- **Blockquotes**: `<blockquote>quoted text</blockquote>` (gray left border, italic)

## Tables

Tables are automatically styled with:
- Blue header background
- Hover effect on rows
- Alternating row colors

```html
<table>
  <tr>
    <th>Header 1</th>
    <th>Header 2</th>
  </tr>
  <tr>
    <td>Data 1</td>
    <td>Data 2</td>
  </tr>
</table>
```

## Responsive Design

The theme includes responsive breakpoints:
- **Desktop**: Full width up to 1200px
- **Tablet/Mobile** (< 768px):
  - Reduced padding
  - Smaller font sizes
  - Adjusted heading sizes

## Print Styles

The theme includes print-optimized styles:
- Removes shadows and backgrounds
- Prevents page breaks in code blocks
- Keeps headings with their content

## Converting Markdown to HTML

### Using Pandoc

```bash
# Basic conversion
pandoc input.md -o output-content.html

# Then wrap with template
template=$(cat html-theme-template.html)
content=$(cat output-content.html)
echo "$template" | \
  sed "s/{{TITLE}}/My Title/" | \
  sed "s|{{CONTENT}}|$content|" > final.html
```

### Using Python (markdown library)

```python
import markdown

# Read markdown
with open('input.md', 'r') as f:
    md_content = f.read()

# Convert to HTML
html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])

# Read template
with open('html-theme-template.html', 'r') as f:
    template = f.read()

# Replace placeholders
output = template.replace('{{TITLE}}', 'My Document Title')
output = output.replace('{{CONTENT}}', html_content)

# Write output
with open('output.html', 'w') as f:
    f.write(output)
```

### Using Node.js (marked library)

```javascript
const fs = require('fs');
const marked = require('marked');

// Read files
const mdContent = fs.readFileSync('input.md', 'utf8');
const template = fs.readFileSync('html-theme-template.html', 'utf8');

// Convert markdown to HTML
const htmlContent = marked.parse(mdContent);

// Replace placeholders
const output = template
  .replace('{{TITLE}}', 'My Document Title')
  .replace('{{CONTENT}}', htmlContent);

// Write output
fs.writeFileSync('output.html', output);
```

## Customization

### Changing Colors

To customize colors, modify the CSS variables in the `<style>` section:

```css
/* Primary colors */
--primary: #3498db;
--success: #27ae60;
--warning: #f39c12;
--danger: #e74c3c;
--info: #16a085;

/* Neutral colors */
--dark: #2c3e50;
--light: #ecf0f1;
--gray: #bdc3c7;
```

### Adjusting Layout

Modify the `.container` class to change the layout:

```css
.container {
    max-width: 1200px;  /* Change max width */
    padding: 40px;      /* Change padding */
    margin: 0 auto;     /* Keep centered */
}
```

### Custom Fonts

Replace the font-family in the `body` selector:

```css
body {
    font-family: 'Your Font', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
}
```

## Best Practices

1. **Use semantic HTML**: Use appropriate heading levels (H1 → H2 → H3)
2. **Box classes**: Use info/warning/success/danger boxes to highlight important content
3. **Code formatting**: Use `<pre><code>` for multi-line code, `<code>` for inline
4. **Tables**: Use tables for structured data, not layout
5. **Badges**: Use badges to highlight status or categories
6. **Section dividers**: Use between major sections for visual separation

## Examples

See `VXLAN-BRIDGE-REMOVAL-PLAN.html` for a complete example implementation showing:
- All box types in use
- Badge usage
- Code blocks (inline and multi-line)
- Tables
- Checklists
- Architecture flow diagrams
- Section dividers
- Responsive design

## Browser Compatibility

The theme is compatible with:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## License

This theme is provided as-is for personal and commercial use.

## Version History

- **v1.0** (2026-06-11): Initial release
  - Web-safe color palette
  - Flat design aesthetic
  - Responsive layout
  - Print styles
  - Multiple box types
  - Badge system
  - Code highlighting
