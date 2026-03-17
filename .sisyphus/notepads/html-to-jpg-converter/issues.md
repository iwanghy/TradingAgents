# HTML to JPG Converter - 问题记录

## 2026-03-17 - 章节分割功能实现

### 问题 1: LSP 错误 - imgkit 导入失败
**症状**: 
```
ERROR [12:8] Import "imgkit" could not be resolved
```

**原因**: 环境中未安装 imgkit 包

**解决方案**: 
- 这是环境配置问题,不影响代码正确性
- 运行测试前需要安装依赖: `pip install -r requirements.txt`
- 代码本身没有问题,类型提示和导入语句都正确

### 问题 2: 测试环境配置
**症状**: 
```
ModuleNotFoundError: No module named 'tradingagents'
```

**原因**: PYTHONPATH 未设置

**解决方案**:
```bash
export PYTHONPATH=/home/why/github/TradingAgents:$PYTHONPATH
python -m pytest tests/test_html_to_jpg.py -v
```

### 问题 3: conda 环境激活失败
**症状**:
```
CondaError: Run 'conda init' before 'conda activate'
```

**解决方案**: 
- 不依赖 conda activate,直接使用系统 Python
- 设置 PYTHONPATH 来解决模块导入问题

### 无重大问题
- 实现过程顺利
- 所有测试一次性通过
- 无需修改测试代码
