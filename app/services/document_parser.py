from __future__ import annotations

from typing import Any

from app.utils.result_utils import make_json_serializable


class DocumentParser:

    @staticmethod
    def _get_result_dict(result: Any) -> dict:

        # PaddleOCR result object
        if hasattr(result, "json"):
            try:
                data = result.json

                if callable(data):
                    data = data()

                if isinstance(data, str):
                    import json
                    data = json.loads(data)

                if isinstance(data, dict):
                    return data

            except Exception:
                pass

        # Alternative result API
        if hasattr(result, "to_json"):
            try:
                data = result.to_json()

                if isinstance(data, str):
                    import json
                    data = json.loads(data)

                if isinstance(data, dict):
                    return data

            except Exception:
                pass

        # Dictionary directly
        if isinstance(result, dict):
            return result

        return {}

    @classmethod
    def parse_results(
        cls,
        results: list[Any]
    ) -> dict:

        pages = []

        for page_number, result in enumerate(
            results,
            start=1
        ):

            raw = cls._get_result_dict(
                result
            )

            raw = make_json_serializable(
                raw
            )

            page = {
                "page_number": page_number,
                "raw": raw,
                "text": cls.extract_text(raw),
                "tables": cls.extract_tables(raw),
                "elements": cls.extract_elements(raw),
            }

            pages.append(page)

        return {
            "page_count": len(pages),
            "pages": pages,
        }

    @staticmethod
    def extract_text(
        data: dict
    ) -> str:

        texts = []

        def walk(value):

            if isinstance(value, dict):

                # PaddleOCR recognition result
                rec_texts = value.get(
                    "rec_texts"
                )

                if isinstance(
                    rec_texts,
                    list
                ):

                    for item in rec_texts:

                        if item is not None:

                            text = str(item).strip()

                            if text:
                                texts.append(text)

                # Generic text fields
                for key in (
                    "text",
                    "texts",
                    "rec_text",
                ):

                    candidate = value.get(key)

                    if isinstance(
                        candidate,
                        str
                    ):

                        candidate = candidate.strip()

                        if candidate:
                            texts.append(candidate)

                    elif isinstance(
                        candidate,
                        list
                    ):

                        for item in candidate:

                            if isinstance(
                                item,
                                str
                            ):

                                item = item.strip()

                                if item:
                                    texts.append(item)

                            elif isinstance(
                                item,
                                dict
                            ):

                                text = item.get(
                                    "text"
                                )

                                if text:

                                    text = str(
                                        text
                                    ).strip()

                                    if text:
                                        texts.append(
                                            text
                                        )

                # Continue recursively
                for child in value.values():
                    walk(child)

            elif isinstance(
                value,
                list
            ):

                for child in value:
                    walk(child)

        walk(data)

        # Remove duplicates while preserving order
        output = []
        seen = set()

        for text in texts:

            text = text.strip()

            if not text:
                continue

            if text in seen:
                continue

            seen.add(text)
            output.append(text)

        return "\n".join(output)

    @staticmethod
    def extract_tables(
        data: dict
    ) -> list:

        tables = []

        def walk(value):

            if isinstance(value, dict):

                for key, child in value.items():

                    key_lower = key.lower()

                    if (
                        "table" in key_lower
                        and child is not None
                    ):

                        if isinstance(
                            child,
                            list
                        ):

                            tables.extend(
                                child
                            )

                        elif isinstance(
                            child,
                            dict
                        ):

                            tables.append(
                                child
                            )

                    walk(child)

            elif isinstance(
                value,
                list
            ):

                for child in value:
                    walk(child)

        walk(data)

        return tables

    @staticmethod
    def extract_elements(
        data: dict
    ) -> list:

        elements = []

        parsing_results = data.get(
            "parsing_res_list"
        )

        if not isinstance(
            parsing_results,
            list
        ):

            return elements

        for item in parsing_results:

            if not isinstance(
                item,
                dict
            ):
                continue

            elements.append({
                "type": item.get(
                    "block_label"
                ),
                "content": item.get(
                    "block_content"
                ),
                "bbox": item.get(
                    "block_bbox"
                ),
                "order": item.get(
                    "block_order"
                ),
                "sub_label": item.get(
                    "sub_label"
                ),
            })

        return elements