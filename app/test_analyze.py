from analyze import analyze_document  # Import directly, without 'app'

# Use raw string or double backslashes for Windows paths
file_path = r"C:\work\GenAI-Home-Assignment-KPMG\phase1_data\283_ex1.pdf"  # Using raw string

try:
    result = analyze_document(file_path)
    print("Extracted Data:", result)
except Exception as e:
    print("Error:", str(e))
