# 🔍 PDF Keyword Scanner

A blazing-fast, multi-core PDF keyword scanner that recursively searches through directories to find PDF documents containing a specific keyword — perfect for forensic investigations, compliance audits, or large-scale document analysis.

## ⚡ Features

- ✅ **Multi-core processing** using `ProcessPoolExecutor`
- 📁 **Recursive directory scanning**
- 📝 **Error logging** with detailed messages
- 📄 **Match logging** to output file
- 🧠 Efficient memory management using batching
- 📊 Real-time progress and performance metrics

## 🚀 Usage

### 1. Requirements

- Python 3.8+
- [`PyMuPDF` (fitz)](https://pymupdf.readthedocs.io/en/latest/)

Install dependencies:
```bash
pip install PyMuPDF
