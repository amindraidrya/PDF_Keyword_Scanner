import os
import fitz
import time
import concurrent.futures
from multiprocessing import cpu_count
from collections import deque

# --- CONFIGURATION ---
FOLDER_PATH = r'C:\path\to\your\pdf\directory'
SEARCH_TERM = "your_keyword".lower()
OUTPUT_FILE = "matching_pdfs.txt"
LOG_FILE = "scan_errors.log"
MAX_WORKERS = min(8, cpu_count()) 
BATCH_SIZE = 1000 
CHUNK_SIZE = 20 

# --- PROCESSING FUNCTIONS ---
def process_pdf(file_path):
    """Process of a single PDF file"""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                if SEARCH_TERM in page.get_text().lower():
                    return file_path
        return None
    except Exception as e:
        with open(LOG_FILE, "a") as log_f:
            log_f.write(f"{file_path} | Error: {str(e)[:200]}\n")
        return None

def process_batch(batch):
    """Process a batch of files"""
    return [result for result in (process_pdf(f) for f in batch) if result]

def get_pdf_files():
    """File enumeration"""
    pdf_files = []
    with os.scandir(FOLDER_PATH) as it:
        for entry in it:
            if entry.is_file() and entry.name.lower().endswith('.pdf'):
                pdf_files.append(entry.path)
            elif entry.is_dir():
                for root, _, files in os.walk(entry.path):
                    for file in files:
                        if file.lower().endswith('.pdf'):
                            pdf_files.append(os.path.join(root, file))
    return pdf_files

# --- MAIN PROCESSING ---
def main():
    print(f"🔍 Starting search for '{SEARCH_TERM}' in {FOLDER_PATH}")
    start_time = time.perf_counter()
    
    # Initialize output files
    with open(OUTPUT_FILE, "w") as out_f, open(LOG_FILE, "w") as log_f:
        out_f.write("")
        log_f.write("PDF Scan Error Log\n\n")
    
    pdf_files = get_pdf_files()
    total_files = len(pdf_files)
    print(f"Found {total_files:,} PDF files to process")
    
    # Parallel processing
    processed = 0
    matches = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Process in chunks to avoid memory issues
        chunks = (pdf_files[i:i + CHUNK_SIZE] 
                 for i in range(0, len(pdf_files), CHUNK_SIZE))
        
        futures = {executor.submit(process_batch, chunk): chunk 
                 for chunk in chunks}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                batch_results = future.result()
                matches.extend(batch_results)
                processed += len(futures[future])
                
                if processed % BATCH_SIZE == 0:
                    elapsed = time.perf_counter() - start_time
                    rate = processed / elapsed
                    print(
                        f"\rProcessed {processed:,}/{total_files:,} files | "
                        f"{rate:.1f} files/sec | Matches: {len(matches)}",
                        end="", flush=True
                    )
            except Exception as e:
                print(f"\nError processing batch: {str(e)}")
    
    with open(OUTPUT_FILE, "w") as out_f:
        out_f.write("\n".join(matches))
    
    # Final report
    elapsed = time.perf_counter() - start_time
    print(f"\n\n🏁 Processing complete in {elapsed:.1f} seconds")
    print(f"📊 Total matches found: {len(matches):,}")
    print(f"📄 Results saved to: {OUTPUT_FILE}")
    print(f"⚠️  Errors logged to: {LOG_FILE}")
    print(f"⚡ Average speed: {total_files/elapsed:.1f} files/sec")

if __name__ == "__main__":
    main()
