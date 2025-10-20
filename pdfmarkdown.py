# pip install -U docling docling-core transformers pillow

from pathlib import Path
import re, json
from typing import List, Dict

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode

# ---- 入力PDF（厚労省） ----
#DOC_SOURCE = "https://www.mhlw.go.jp/content/001018385.pdf"  # ユーザ指定URL
DOC_SOURCE="C:\\WorkSpace\\HandsOnTest\\001018385.pdf"
# ---- Doclingの変換設定（表をMarkdown化しやすく）----
pipeline_options = PdfPipelineOptions(
    do_table_structure=True,   # 表構造を復元（Markdownテーブル品質↑）
)
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE  # 精度重視
# 画像はピクセル出力しない（キャプションだけを後処理で残す）
pipeline_options.generate_page_images = False
pipeline_options.generate_picture_images = False
# （スキャンPDFなら）OCRを使う場合は↓を有効化し、日本語モデルを指定
# from docling.datamodel.pipeline_options import OcrEngine
# pipeline_options.do_ocr = True
# pipeline_options.ocr_options.lang = ["jpn"]

converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)

result = converter.convert(DOC_SOURCE)
dl_doc = result.document

# ---- Markdownを取得（画像参照は付けない）----
# Serializerを直呼びでもOK：dl_doc.export_to_markdown()
md_text = dl_doc.export_to_markdown()

# ---- 「画像キャプションだけ残す」後処理
# 例： ![図1　○○](path/to/img.png) → 図: 図1　○○
def strip_image_links_keep_captions(md: str) -> str:
    # ![caption](url) を "図: caption" に置換
    pattern = re.compile(r'!\[(?P<cap>[^\]]*)\]\([^)]+\)')
    return pattern.sub(lambda m: f"図: {m.group('cap')}".strip(), md)

md_caption_only = strip_image_links_keep_captions(md_text)

# ---- 章（見出し）ごとに分割（# が無ければ ## で分割）
def split_markdown_into_chapters(md: str) -> List[Dict]:
    if re.search(r'^\#\s+', md, flags=re.MULTILINE):
        splitter = re.compile(r'(?m)^(?P<h>\#\s+[^\n]+)\s*\n')
        level = 1
    else:
        splitter = re.compile(r'(?m)^(?P<h>\#\#\s+[^\n]+)\s*\n')
        level = 2

    parts = []
    idx = 0
    matches = list(splitter.finditer(md))
    if not matches:
        # 見出しが無ければ全文を1章扱い
        return [{"level": 0, "title": "全文", "text": md.strip()}]

    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        title = re.sub(r'^\#\#?\s+', '', m.group('h')).strip()
        body = md[start:end].strip()
        if body:
            parts.append({"level": level, "title": title, "text": body})
        idx = end
    return parts

chapters = split_markdown_into_chapters(md_caption_only)

# ---- 保存（任意）：Markdown全文 & 章ごとのJSONL（ベクトル投入向け）
out_dir = Path("C:\WorkSpace\HandsOnTest\out_mhlw")
out_dir.mkdir(parents=True, exist_ok=True)

(out_dir / "mhlw_full_caption_only.md").write_text(md_caption_only, encoding="utf-8")

with (out_dir / "mhlw_chapters.jsonl").open("w", encoding="utf-8") as f:
    for ch in chapters:
        f.write(json.dumps(ch, ensure_ascii=False) + "\n")

print(f"Markdown（キャプションのみ）: {out_dir/'mhlw_full_caption_only.md'}")
print(f"章ごとJSONL: {out_dir/'mhlw_chapters.jsonl'}")
print(f"章数: {len(chapters)}")
