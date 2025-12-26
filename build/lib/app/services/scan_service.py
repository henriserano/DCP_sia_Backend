from __future__ import annotations

from typing import Any, Dict, List

from app.connectors.filesystem import FileSystemConnector
from app.extractors.dispatcher import ExtractorDispatcher
from app.services.pipeline_text import TextPipeline
from app.services.pipeline_images import ImagePipeline
from app.services.pipeline_docs import DocumentPipeline
from app.services.scoring import summarize


class ScanService:
    def __init__(self) -> None:
        self.fs = FileSystemConnector()
        self.extractor = ExtractorDispatcher()

        self.text_pipeline = TextPipeline()
        self.doc_pipeline = DocumentPipeline()
        self.img_pipeline = ImagePipeline()

    def scan(
        self,
        *,
        connector: str,
        root: str,
        recursive: bool,
        language: str,
        detectors: List[str],
        min_score: float,
        limit: int = 200,
    ) -> Dict[str, Any]:
        if connector != "filesystem":
            raise ValueError("Only connector=filesystem is supported for now")

        resources = list(self.fs.list(root, recursive=recursive))[: max(0, limit)]
        results: List[Dict[str, Any]] = []
        global_spans = []

        for r in resources:
            # Strategy:
            # - for documents/images: use pipelines (they handle extraction)
            # - for text files: read directly and detect
            if r.kind == "document":
                spans, _, summary, errors = self.doc_pipeline.detect_file(
                    file_path=r.uri.replace("file://", ""),
                    language=language,
                    detectors=detectors,
                    min_score=min_score,
                    merge_overlaps=True,
                    return_text=False,
                )
                global_spans.extend(spans)
                results.append({"uri": r.uri, "kind": r.kind, "summary": summary, "errors": errors, "count": len(spans)})

            elif r.kind == "image":
                try:
                    spans, _, summary, errors = self.img_pipeline.detect_image(
                        image_path=r.uri.replace("file://", ""),
                        language=language,
                        detectors=detectors,
                        min_score=min_score,
                        merge_overlaps=True,
                    )
                    global_spans.extend(spans)
                    results.append({"uri": r.uri, "kind": r.kind, "summary": summary, "errors": errors, "count": len(spans)})
                except Exception as e:
                    results.append({"uri": r.uri, "kind": r.kind, "summary": {}, "errors": {"ocr": str(e)}, "count": 0})

            else:
                text = self.fs.read_text(r.uri)
                spans, _, summary, errors = self.text_pipeline.detect(
                    text=text,
                    language=language,
                    detectors=detectors,
                    min_score=min_score,
                    merge_overlaps=True,
                    return_text=False,
                    best_effort=True,
                )
                global_spans.extend(spans)
                results.append({"uri": r.uri, "kind": r.kind, "summary": summary, "errors": errors, "count": len(spans)})

        return {
            "scanned": len(resources),
            "results": results,
            "summary": summarize(global_spans),
        }