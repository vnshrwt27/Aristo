from pathlib import Path
from tools.base import Tools

class ReadFileTool(Tools):
    name = "read_file",
    description="Reads File attached to query"
    input_schema={
            "path" : "string" 
            }
    output_schema= {
            "content": "string"
            }
    def run(self, path:str) -> dict:
        file_path=Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not Found:{path}")
        if not file_path.is_file():
            raise ValueError(f"Not a file:{file_path}")

        content = file_path.read_text(encoding="utf-8", errors="ignore")
        
        return {
                "content": content
                } 
        
    
