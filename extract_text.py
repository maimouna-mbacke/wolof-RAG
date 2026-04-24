import os
from pathlib import Path
import PyPDF2

# Configuration
INPUT_DIR = "Wolof_Resources"
OUTPUT_DIR = "Wolof_Resources_Text"


def extract_text_from_pdf(pdf_path):
    """Extract text from a single PDF file."""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)

            print(f"    Processing {num_pages} pages...")

            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += f"\n{'=' * 60}\n"
                text += f"PAGE {page_num + 1}\n"
                text += f"{'=' * 60}\n\n"
                text += page.extract_text()
                text += "\n\n"

        return text, True

    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return None, False


def create_output_structure():
    """Create output directory structure mirroring input."""
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    input_path = Path(INPUT_DIR)
    for category_dir in input_path.iterdir():
        if category_dir.is_dir():
            (output_path / category_dir.name).mkdir(exist_ok=True)

    print(f"✓ Created output directory: '{OUTPUT_DIR}/'")


def process_all_pdfs():
    """Process all PDFs and extract text."""
    create_output_structure()

    stats = {"total": 0, "success": 0, "failed": 0}

    input_path = Path(INPUT_DIR)
    output_path = Path(OUTPUT_DIR)

    # Walk through all directories
    for category_dir in sorted(input_path.iterdir()):
        if not category_dir.is_dir():
            continue

        print(f"\n{'=' * 60}")
        print(f"Category: {category_dir.name}")
        print(f"{'=' * 60}")

        pdf_files = list(category_dir.glob("*.pdf"))

        if not pdf_files:
            print("  No PDF files found in this category.")
            continue

        for pdf_file in sorted(pdf_files):
            stats["total"] += 1
            print(f"\n  📄 {pdf_file.name}")

            # Define output file path
            txt_filename = pdf_file.stem + ".txt"
            output_file = output_path / category_dir.name / txt_filename

            # Check if already processed
            if output_file.exists():
                print(f"    ⊙ Skipping (already extracted)")
                stats["success"] += 1
                continue

            # Extract text
            text, success = extract_text_from_pdf(pdf_file)

            if success and text:
                # Save to text file
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(f"Source: {pdf_file.name}\n")
                        f.write(f"Extracted: {Path(pdf_file).stat().st_mtime}\n")
                        f.write(f"\n{'=' * 60}\n\n")
                        f.write(text)

                    print(f"    ✓ Extracted to: {txt_filename}")
                    stats["success"] += 1

                except Exception as e:
                    print(f"    ✗ Failed to save: {str(e)}")
                    stats["failed"] += 1
            else:
                stats["failed"] += 1

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"EXTRACTION SUMMARY")
    print(f"{'=' * 60}")
    print(f"Total PDFs: {stats['total']}")
    print(f"✓ Successfully extracted: {stats['success']}")
    print(f"✗ Failed: {stats['failed']}")
    print(f"\nText files saved to: {Path(OUTPUT_DIR).absolute()}")


def main():
    """Main function."""
    print("=" * 60)
    print("PDF TEXT EXTRACTOR FOR WOLOF RESOURCES")
    print("=" * 60)
    print(f"\nExtracting text from PDFs in '{INPUT_DIR}/'")
    print(f"Saving to '{OUTPUT_DIR}/'\n")

    # Check if input directory exists
    if not Path(INPUT_DIR).exists():
        print(f"✗ Error: Directory '{INPUT_DIR}' not found!")
        print(f"  Make sure you've run the download script first.")
        return

    try:
        process_all_pdfs()
        print("\n✓ Text extraction completed!")
        print(f"\nYou can now find all extracted text in the '{OUTPUT_DIR}' folder.")

    except KeyboardInterrupt:
        print("\n\n⚠ Extraction interrupted by user")
    except Exception as e:
        print(f"\n✗ An error occurred: {str(e)}")


if __name__ == "__main__":
    main()