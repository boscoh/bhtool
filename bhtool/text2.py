#!/usr/bin/env python3

"""cli convert between md|html|docx|pug"""

from path import Path

from bhtool.utils import run, run_output


def convert_md_to_html(md, html):
    run(f"pandoc --from markdown --to html '{md}' -o '{html}'")
    txt = run_output(f"beautify {html}")
    Path(html).write_text(txt)


def convert_md_to_docx(md, docx):
    run(f"pandoc --from markdown --to docx '{md}' -o '{docx}'")


def convert_docx_to_md(docx, md):
    run(f"pandoc --from docx --to markdown '{docx}' -o '{md}'")


def convert_html_to_pug(html, pug):
    run(f"html2pug < {html} > {pug}")


def convert_pug_to_html(pug, html):
    temp_pug = Path(pug).with_suffix(".temp.pug")
    Path(pug).copy2(temp_pug)
    temp_html = temp_pug.with_suffix(".html")
    if temp_html.exists():
        temp_html.unlink()
    run(f"pug {temp_pug}  ")
    txt = run_output(f"beautify {temp_html}")
    Path(html).write_text(txt)


def convert_html_to_md(html, md):
    run(f"pandoc --from html --to markdown {html} -o {md}")


def text2_run(in_fname: str, out_fname: str):
    in_fname = Path(in_fname)
    out_fname = Path(out_fname)

    in_ext = in_fname.suffix.lower()
    out_ext = out_fname.suffix.lower()
    if (in_ext, out_ext) == (".md", ".pug"):
        temp_html_fname = in_fname.with_suffix(".temp.html")
        convert_md_to_html(in_fname, temp_html_fname)
        convert_html_to_pug(temp_html_fname, out_fname)
    elif (in_ext, out_ext) == (".pug", ".md"):
        temp_html_fname = in_fname.with_suffix(".temp.html")
        convert_pug_to_html(in_fname, temp_html_fname)
        convert_html_to_md(temp_html_fname, out_fname)
    elif (in_ext, out_ext) == (".pug", ".html"):
        convert_pug_to_html(in_fname, out_fname)
    elif (in_ext, out_ext) == (".md", ".html"):
        convert_md_to_html(in_fname, out_fname)
    elif (in_ext, out_ext) == (".md", ".docx"):
        convert_md_to_docx(in_fname, out_fname)
    elif (in_ext, out_ext) == (".docx", ".md"):
        convert_docx_to_md(in_fname, out_fname)
    else:
        print(f"Error: can't handle .suffix: {in_fname} -> {out_fname}")

    print(f">>> Made {out_fname}")
