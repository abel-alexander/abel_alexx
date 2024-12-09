import fitz  # PyMuPDF

# Load the PDF
pdf_path = "Apparel_2PIB.pdf"
doc = fitz.open(pdf_path)

# Analyze the first page (assuming it contains the ToC)
toc_page_number = 0  # Adjust if ToC is not the first page
toc_page = doc[toc_page_number]

# Extract text from the ToC page
toc_text = toc_page.get_text("text")
print("Extracted ToC Text:\n", toc_text)

# Extract hyperlinks from the ToC page
links = toc_page.get_links()

# Function to map a link to the associated text
def get_text_near_link(link_rect, text_blocks):
    """Find the text block closest to the link rectangle."""
    closest_text = None
    min_distance = float("inf")
    for block in text_blocks:
        x0, y0, x1, y1, text, *rest = block  # Adjust to unpack extra values
        distance = abs(link_rect[1] - y1)  # Compare vertical positions
        if distance < min_distance:
            min_distance = distance
            closest_text = text
    return closest_text.strip() if closest_text else "No text found"

# Extract text blocks (text with their positions)
text_blocks = toc_page.get_text("blocks")  # Get text with positions

# Print the structure of text_blocks (debugging)
print("Text Blocks:")
for block in text_blocks:
    print(block)

# Iterate over links and associate them with the ToC text
for i, link in enumerate(links):
    if "page" in link:
        destination_page = link["page"]
        rect = link["from"]  # The rectangle where the link is on the ToC page
        related_text = get_text_near_link(rect, text_blocks)
        print(f"Link {i+1} points to page {destination_page + 1} (1-indexed).")
        print(f"Associated text: {related_text}")

        # Optionally extract text from the destination page
        linked_page = doc[destination_page]
        page_text = linked_page.get_text("text")
        snippet = " ".join(page_text.split()[:50])  # First 50 words
        print(f"Content snippet of page {destination_page + 1}:\n{snippet}\n")
    elif "uri" in link:
        uri = link["uri"]
        print(f"Link {i+1} points to external URL: {uri}")
    else:
        print(f"Link {i+1} has an unknown or unsupported type.")

# Close the document
doc.close()
