from docling.datamodel import vlm_model_specs
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    VlmPipelineOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.pipeline.vlm_pipeline import VlmPipeline
from docling.pipeline.base_pipeline import PdfPipelineOptions

# Convert a public arXiv PDF; replace with a local path if preferred.
source = "https://arxiv.org/pdf/2501.17887"

###### USING SIMPLE DEFAULT VALUES
# - GraniteDocling model
# - Using the transformers framework

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(
        pipeline_options=PdfPipelineOptions(
            generate_picture_images=False,
            do_picture_description=True,
        )
    )
})
print(converter)
doc = converter.convert(source=source).document


            
          # Docling provides pictures through document.pictures
if hasattr(doc, 'pictures'):
    for pic_idx, picture in enumerate(doc.pictures):
        image_info = {
                        'image_id': pic_idx,
                        'caption': picture.caption if hasattr(picture, 'caption') else '',
                        'text': picture.text if hasattr(picture, 'text') else '',  # AI-generated description
                    }
        print(image_info)