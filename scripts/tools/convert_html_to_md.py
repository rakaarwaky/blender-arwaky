#!/usr/bin/env python3
"""Convert downloaded Blender HTML documentation files into clean modular Markdown files by extracting main article content."""

import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag


def tag_to_markdown(element) -> str:
    """Recursively convert HTML element tags to clean Markdown."""
    if isinstance(element, NavigableString):
        text = str(element)
        # Preserve newlines in code blocks
        if element.parent and element.parent.name in ['pre', 'code']:
            return text
        return re.sub(r'\s+', ' ', text)

    if not isinstance(element, Tag):
        return ""

    tag_name = element.name

    # Skip unwanted tags
    if tag_name in ['script', 'style', 'nav', 'aside', 'header', 'footer']:
        return ""

    # Header tags
    if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        level = int(tag_name[1])
        # Strip trailing paragraph symbol '¶'
        inner_text = "".join(tag_to_markdown(child) for child in element.children).replace('¶', '').strip()
        return f"\n\n{'#' * level} {inner_text}\n\n"

    # Paragraph tag
    if tag_name == 'p':
        inner_text = "".join(tag_to_markdown(child) for child in element.children).replace('¶', '').strip()
        if not inner_text:
            return ""
        return f"\n\n{inner_text}\n\n"

    # Preformatted Code Block
    if tag_name == 'pre':
        code_text = element.get_text()
        return f"\n\n```python\n{code_text.strip()}\n```\n\n"

    # Inline Code
    if tag_name == 'code' and element.parent and element.parent.name != 'pre':
        code_text = element.get_text()
        return f"`{code_text.strip()}`"

    # List items
    if tag_name == 'li':
        inner_text = "".join(tag_to_markdown(child) for child in element.children).strip()
        return f"\n- {inner_text}"

    # Links
    if tag_name == 'a':
        href = element.get('href', '')
        link_text = "".join(tag_to_markdown(child) for child in element.children).replace('¶', '').strip()
        if not link_text:
            return ""
        return f"[{link_text}]({href})" if href and not href.startswith('#') else link_text

    # Default fallback: concatenate children
    return "".join(tag_to_markdown(child) for child in element.children)


def convert_html_file(html_path: Path, out_base_dir: Path):
    filename_no_ext = html_path.stem

    # Determine subfolder module category based on filename prefix
    if filename_no_ext.startswith("bpy.ops"):
        category = "bpy.ops"
    elif filename_no_ext.startswith("bpy.types"):
        category = "bpy.types"
    elif filename_no_ext.startswith("bpy.data"):
        category = "bpy.data"
    elif filename_no_ext.startswith("bpy.context"):
        category = "bpy.context"
    elif filename_no_ext.startswith("bpy.app"):
        category = "bpy.app"
    elif filename_no_ext.startswith("bpy.path") or filename_no_ext.startswith("bpy.utils") or filename_no_ext.startswith("bpy.props"):
        category = "bpy.utils_props"
    elif filename_no_ext.startswith("bmesh"):
        category = "bmesh"
    elif filename_no_ext.startswith("mathutils"):
        category = "mathutils"
    elif filename_no_ext.startswith("gpu"):
        category = "gpu"
    elif filename_no_ext.startswith("info_"):
        category = "guides"
    else:
        category = "core"

    cat_dir = out_base_dir / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    out_md_path = cat_dir / f"{filename_no_ext}.md"

    try:
        html_content = html_path.read_text(encoding="utf-8", errors="ignore")
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find main article element
        article = soup.find('article') or soup.find(role='main') or soup.find('div', class_='body')
        if not article:
            return

        raw_md = tag_to_markdown(article)
        clean_md = re.sub(r'\n{3,}', '\n\n', raw_md).strip()

        if clean_md:
            out_md_path.write_text(f"# {filename_no_ext}\n\n{clean_md}\n", encoding="utf-8")

    except Exception as e:
        print(f"Error converting {html_path}: {e}")


def main():
    base_dir = Path("/home/raka/mcp-arwaky/blender-arwaky")
    html_src_dir = base_dir / "docs/blender_python_api_offline/blender_python_reference_5_2"
    out_md_dir = base_dir / "docs/bpy_md_docs"

    if not html_src_dir.exists():
        print("HTML source directory does not exist.")
        return

    print("Cleaning and regenerating clean Markdown files from main article tags...")
    count = 0
    for html_file in html_src_dir.glob("*.html"):
        convert_html_file(html_file, out_md_dir)
        count += 1

    print(f"Successfully converted {count} HTML files into clean Markdown in {out_md_dir}")


if __name__ == "__main__":
    main()
