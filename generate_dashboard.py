import click
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

NAVBAR_STYLE = """
<style id="wr-styles">
    :root {
        --wr-primary: #1a73e8;
        --wr-bg: #f8f9fa;
        --wr-surface: #ffffff;
        --wr-text-main: #202124;
        --wr-text-subtle: #5f6368;
        --wr-border: #dadce0;
        --wr-shadow: 0 4px 12px rgba(60,64,67, 0.15), 0 1px 3px rgba(60,64,67, 0.3);
    }
    .wr-navbar {
        position: sticky;
        top: 0;
        background: var(--wr-surface);
        padding: 1rem 2rem;
        border-bottom: 1px solid var(--wr-border);
        display: flex;
        align-items: center;
        font-family: 'Roboto', 'Arial', sans-serif;
        justify-content: space-between;
    }
    .wr-navbar__link {
        display: flex;
        align-items: center;
        gap: 12px;
        color: var(--wr-primary);
        text-decoration: none;
    }
    .wr-navbar__linkTitleContainer {
        display: flex;
        align-items: center;
    }
    .wr-navbar__title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        margin-left: 8px;
        color: var(--wr-text-main);
    }
    .wr-navbar__branch {
        color: inherit;
        text-decoration: none;
        margin-left: 4px;
        opacity: 0.8;
    }
    .wr-navbar__branch:hover {
        text-decoration: underline;
    }
    .wr-navbar__branchContainer {
        display: flex;
    }
    @media screen and (max-width: 768px) {
        #agent_case_results {
            margin: 0 !important;
        }
        #master_report_header {
            margin: 10 px!important;
        }
    }
</style>
"""

FONT_LINKS = """
<link id="wr-font-material" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,400,0,0" rel="stylesheet">
"""


def format_navbar_html(root_path, branch_name=None):
    branch_html = ""
    if branch_name:
        branch_html = f"""
        <div class="wr-navbar__branchContainer">
            <span class="material-symbols-outlined" style="opacity: 0.7;">commit</span>
            <a class="wr-navbar__branch" href="https://github.com/odoo-dev/odoo/tree/{branch_name}" target="_blank">{branch_name}</a>
        </div>"""
    return f"""<header id="wr-navbar" class="wr-navbar">
    <a href="{root_path}" class="wr-navbar__link">
        <div class="wr-navbar__linkTitleContainer">
            <span class="material-symbols-outlined" style="font-size: 28px;">lan</span>
            <h1 class="wr-navbar__title">WebSocket Autobahn Reports</h1>
        </div>
    </a>{branch_html}
</header>"""


DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {font_links}
    <title>WebSocket Autobahn Reports</title>
    {style_block}
    <style>
        body {{ margin: 0; background-color: var(--wr-bg); color: var(--wr-text-main); font-family: 'Roboto', sans-serif; }}
        .wr-container {{ max-width: 850px; margin: 40px auto; padding: 0 20px; }}
        .wr-status {{ margin-bottom: 16px; padding: 0 8px; font-size: 0.85rem; color: var(--wr-text-subtle); text-transform: uppercase; font-weight: 600; }}
        .wr-list {{ display: flex; flex-direction: column; gap: 12px; }}
    </style>
</head>
<body>
    {navbar_block}
    <main class="wr-container">
        <div class="wr-status">{count} Reports</div>
        <div class="wr-list">{items}</div>
    </main>
</body>
</html>
"""

REPORT_LINK_TEMPLATE = """
<style>
    .wr-item {{
        background: var(--wr-surface);
        border: 1px solid var(--wr-border);
        border-radius: 8px;
        padding: 16px 20px;
        text-decoration: none;
        color: inherit;
        display: flex;
        align-items: center;
        transition: box-shadow 0.2s, border-color 0.2s;
    }}
    .wr-item:hover {{ box-shadow: var(--wr-shadow); border-color: transparent; }}
    .wr-item__icon {{ background: #e8f0fe; color: var(--wr-primary); width: 42px; height: 42px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 20px; }}
    .wr-item__info {{ flex-grow: 1; }}
    .wr-item__name {{ font-weight: 500; display: block; margin-bottom: 2px; }}
    .wr-item__meta {{ font-size: 0.8rem; color: var(--wr-text-subtle); }}
    .wr-item__chevron {{ color: #bdc1c6; }}
    .wr-item:hover .wr-item__chevron {{ color: var(--wr-primary); }}
</style>
<a href="./{name}/index.html" class="wr-item">
    <div class="wr-item__icon"><span class="material-symbols-outlined">folder_open</span></div>
    <div class="wr-item__info">
        <span class="wr-item__name">{name}</span>
        <span class="wr-item__meta">Modified: {date}</span>
    </div>
    <span class="material-symbols-outlined wr-item__chevron">arrow_forward_ios</span>
</a>
"""


def patch_file(file_path, root_dir):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    folder_name = file_path.relative_to(root_dir).parts[0]
    report_title = f"WR - {folder_name}"
    if soup.title:
        soup.title.decompose()
    title = soup.new_tag("title")
    title.string = report_title
    soup.head.insert(0, title)
    for selector in [
        ("header", {"id": "wr-navbar"}),
        ("style", {"id": "wr-styles"}),
        ("link", {"id": "wr-font-material"}),
        ("meta", {"name": "viewport"}),
    ]:
        for tag in soup.head.find_all(selector[0], attrs=selector[1]):
            tag.decompose()
    soup.head.append(
        BeautifulSoup(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            "html.parser",
        ),
    )
    soup.head.append(BeautifulSoup(FONT_LINKS, "html.parser"))
    soup.head.append(BeautifulSoup(NAVBAR_STYLE, "html.parser"))
    folder_name = file_path.relative_to(root_dir).parts[0]
    depth = len(file_path.relative_to(root_dir).parts) - 1
    rel_root = ("../" * depth) + "index.html"
    nav_html = format_navbar_html(root_path=rel_root, branch_name=folder_name)
    if header := soup.body.find("header", id="wr-navbar"):
        header.decompose()
    soup.body.insert(0, BeautifulSoup(nav_html, "html.parser"))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))


@click.command()
def generate_dashboard():
    base = Path.cwd() / "reports"
    items_html = []
    report_dirs = [d for d in base.iterdir() if d.is_dir()]
    report_dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    for rdir in report_dirs:
        mtime = rdir.stat().st_mtime
        formatted_date = datetime.fromtimestamp(mtime).strftime("%b %d, %Y %H:%M")
        items_html.append(REPORT_LINK_TEMPLATE.format(name=rdir.name, date=formatted_date))
        for html_file in rdir.rglob("index.html"):
            patch_file(html_file, base)
    output_file = base / "index.html"
    final_html = DASHBOARD_TEMPLATE.format(
        style_block=NAVBAR_STYLE,
        font_links=FONT_LINKS,
        navbar_block=format_navbar_html(root_path="./index.html"),
        count=len(items_html),
        items="\n".join(items_html),
    )
    output_file.write_text(final_html, encoding="utf-8")


if __name__ == "__main__":
    generate_dashboard()
