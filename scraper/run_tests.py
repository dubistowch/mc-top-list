"""測試執行腳本"""

import unittest
import sys
from pathlib import Path

def run_tests():
    """執行所有測試"""
    # 設定測試目錄
    test_dir = Path(__file__).parent / "tests"
    if not test_dir.exists():
        print("找不到測試目錄")
        sys.exit(1)
    
    # 載入所有測試
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir))
    
    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 根據測試結果設定退出碼
    sys.exit(not result.wasSuccessful())

if __name__ == "__main__":
    run_tests() 