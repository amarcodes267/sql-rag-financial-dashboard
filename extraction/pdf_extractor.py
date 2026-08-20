import fitz


def extract_text_from_pdf(file_path):
    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document):
        text = page.get_text()

        if text.strip():
            pages.append({
                "page": page_number + 1,
                "text": text
            })

    document.close()

    return pages


def combine_pages(pages):
    return "\n\n".join(
        f"PAGE {page['page']}\n{page['text']}"
        for page in pages
    )