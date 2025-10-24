#!/usr/bin/env python3
"""
PDF to Text Converter for DRAGINO Documentation
Extracts text from PDF files in the current directory and saves as .txt files
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if required libraries are available, install if needed"""
    try:
        import PyPDF2
    except ImportError:
        print("PyPDF2 not found. Installing...")
        os.system("pip install PyPDF2")
        try:
            import PyPDF2
        except ImportError:
            print("Failed to install PyPDF2. Please install manually: pip install PyPDF2")
            return False
    
    return True

def pdf_to_text(pdf_path, output_path=None):
    """
    Extract text from PDF file and save to text file
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Path for output text file. 
                                   If None, uses same name as PDF with .txt extension
    """
    try:
        import PyPDF2
        
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file '{pdf_path}' not found.")
            return False
            
        if output_path is None:
            # Create output filename by replacing .pdf with .txt
            output_path = str(Path(pdf_path).with_suffix('.txt'))
        
        print(f"Processing: {pdf_path}")
        print(f"Output will be saved to: {output_path}")
        
        # Open PDF file
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            full_text = ""
            total_pages = len(pdf_reader.pages)
            
            print(f"Total pages: {total_pages}")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    page_text = page.extract_text()
                    full_text += f"\n--- Page {page_num} ---\n"
                    full_text += page_text
                    full_text += "\n"
                    print(f"Extracted page {page_num}/{total_pages}")
                except Exception as e:
                    print(f"Error extracting page {page_num}: {e}")
                    continue
        
        # Save extracted text
        with open(output_path, 'w', encoding='utf-8') as text_file:
            # Add header with source information
            text_file.write(f"Extracted from: {pdf_path}\n")
            text_file.write(f"Total pages: {total_pages}\n")
            text_file.write("=" * 80 + "\n\n")
            text_file.write(full_text)
        
        print(f"Successfully extracted text to: {output_path}")
        print(f"Total characters extracted: {len(full_text)}")
        
        return True
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return False

def find_and_process_pdfs():
    """Find all PDF files in current directory and convert them"""
    current_dir = Path(".")
    pdf_files = list(current_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in current directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s):")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file}")
    
    print("\nProcessing PDF files...")
    
    for pdf_file in pdf_files:
        success = pdf_to_text(str(pdf_file))
        if success:
            print(f"✓ Processed: {pdf_file}")
        else:
            print(f"✗ Failed to process: {pdf_file}")
        print()

def main():
    """Main function"""
    print("PDF to Text Converter for DRAGINO Documentation")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Find and process PDFs
    find_and_process_pdfs()
    
    print("Processing complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())


