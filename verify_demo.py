import sys
from pathlib import Path
from io import StringIO
from unittest.mock import patch

# Mocking input and capturing output
def run_demo_test(input_text):
    # Set up paths
    repo_root = Path(__file__).parent.absolute()
    src_path = repo_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))

    from brain_bee.main import main

    with patch('sys.stdin', StringIO(input_text)):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            try:
                main()
            except SystemExit:
                pass
            return fake_out.getvalue()

if __name__ == "__main__":
    print("--- Test 1: Simple Message ---")
    out1 = run_demo_test("你好\nexit\n")
    print(out1)
    
    print("\n--- Test 2: Task Message ---")
    out2 = run_demo_test("帮我分析一下这个项目的代码质量\nexit\n")
    print(out2)
