"""
自动迁移到新的日志系统

将所有 Python 文件中的 logging 替换为新的 loguru 日志系统
"""

import os
import re
from pathlib import Path

def migrate_file(file_path: Path) -> bool:
    """迁移单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. 替换 import logging
        if 'import logging' in content and 'from api.core.logger import logger' not in content:
            # 移除 import logging
            content = re.sub(r'^import logging\n', '', content, flags=re.MULTILINE)
            
            # 移除 logger = logging.getLogger(__name__)
            content = re.sub(r'^logger = logging\.getLogger\(__name__\)\n', '', content, flags=re.MULTILINE)
            
            # 在合适的位置添加新的导入
            # 找到最后一个 from api. 导入的位置
            api_imports = list(re.finditer(r'^from api\..*\n', content, flags=re.MULTILINE))
            if api_imports:
                last_import = api_imports[-1]
                insert_pos = last_import.end()
                content = content[:insert_pos] + 'from api.core.logger import logger\n' + content[insert_pos:]
            else:
                # 如果没有 api 导入,在第一个 import 后添加
                first_import = re.search(r'^(from .* import .*|import .*)\n', content, flags=re.MULTILINE)
                if first_import:
                    insert_pos = first_import.end()
                    content = content[:insert_pos] + 'from api.core.logger import logger\n' + content[insert_pos:]
        
        # 只有内容改变时才写入
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"❌ 处理文件失败 {file_path}: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("开始迁移到新的日志系统")
    print("=" * 60)
    print()
    
    # 需要迁移的目录
    directories = [
        Path("api"),
        Path("medical_agent"),
    ]
    
    migrated_files = []
    skipped_files = []
    
    for directory in directories:
        if not directory.exists():
            continue
        
        # 遍历所有 Python 文件
        for py_file in directory.rglob("*.py"):
            # 跳过 __pycache__ 和已经是 logger.py 的文件
            if '__pycache__' in str(py_file) or py_file.name == 'logger.py':
                continue
            
            print(f"处理: {py_file}")
            
            if migrate_file(py_file):
                migrated_files.append(py_file)
                print(f"  ✓ 已迁移")
            else:
                skipped_files.append(py_file)
                print(f"  - 跳过(无需修改)")
    
    print()
    print("=" * 60)
    print("迁移完成!")
    print("=" * 60)
    print(f"✓ 已迁移: {len(migrated_files)} 个文件")
    print(f"- 跳过: {len(skipped_files)} 个文件")
    print()
    
    if migrated_files:
        print("已迁移的文件:")
        for f in migrated_files:
            print(f"  - {f}")

if __name__ == "__main__":
    main()
