
import logging
from sys import exception
import time
from pathlib import Path
import json

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc.document import SectionHeaderItem

_log = logging.getLogger(__name__)

IMAGE_RESOLUTION_SCALE = 2.0


def build_tree(doc):

    root = {
        "type": "document",
        "title": None ,
        "text": None,
        "children": [],
        "level": -1
    }

    stack = [root]

    for item, level in doc.iterate_items():

        text = getattr(item ,"text" ,None ) or getattr(item ,"orig" ,None)
        if not root["title"] and getattr(item , "label",None) == "section_header":
            title = getattr(item ,"orig" ,None) 
            root["title"] = title 
        node = {
            "id": item.self_ref,
            "type": item.label.value,
            "text": text,
            "page": item.prov[0].page_no if item.prov else None,
            "children": [],
            "level": level
        }

        # move up until we find correct parent
        while stack and stack[-1]["level"] >= level:
            stack.pop()

        stack[-1]["children"].append(node)
        stack.append(node)

    return root


def main():
    logging.basicConfig(level=logging.INFO)

    data_folder = Path(__file__).parent / "../../tests/data"
    input_doc_path = data_folder / "/home/itzfranku/Aristo/2408.09869v5.pdf"
    output_dir = Path("scratch")

    # Keep page/element images so they can be exported. The `images_scale` controls
    # the rendered image resolution (scale=1 ~ 72 DPI). The `generate_*` toggles
    # decide which elements are enriched with images.
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = doc_converter.convert(input_doc_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_res.input.file.stem


    doc = conv_res.document


    tree = build_tree(doc)

    with open("doc_tree.json", "w", encoding = "utf-8") as f:
        json.dump( tree , f, indent = 4)
        print("Tree Saved")

    #print(tree)


    # Save page images
    for page_no, page in conv_res.document.pages.items():
        page_no = page.page_no
        page_image_filename = output_dir / f"{doc_filename}-{page_no}.png"
        with page_image_filename.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")

    # Save images of figures and tables
    table_counter = 0
    picture_counter = 0
    for element, _level in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-table-{table_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            )
            with element_image_filename.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

    # Save markdown with embedded pictures
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    # Save markdown with externally referenced pictures
    md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_res.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    # Save HTML with externally referenced pictures
    html_filename = output_dir / f"{doc_filename}-with-image-refs.html"
    conv_res.document.save_as_html(html_filename, image_mode=ImageRefMode.REFERENCED)

    end_time = time.time() - start_time

    _log.info(f"Document converted and figures exported in {end_time:.2f} seconds.")


if __name__ == "__main__":
    main()
