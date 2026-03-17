# HTML to JPG Converter - 未解决问题

## 2026-03-17 - 章节分割功能

### 无重大未解决问题

当前实现完整且测试通过,无关键问题需要解决。

### 潜在改进点 (非阻塞)

#### 1. 图片质量控制
**当前**: 固定 quality=85  
**潜在**: 根据内容动态调整质量,或允许用户自定义每个片段的质量

**优先级**: 低  
**理由**: 当前质量已满足大部分需求

#### 2. 片段高度自适应
**当前**: 简单按 section 分割,不考虑高度  
**潜在**: 如果某个 section 过长,可以进一步分割

**优先级**: 低  
**理由**: 增加复杂度,当前按 section 分割已满足需求

#### 3. 样式优化
**当前**: 每个片段复制完整 style 标签  
**潜在**: 将样式提取为外部 CSS 文件,减少重复

**优先级**: 低  
**理由**: 当前实现简单且有效,优化收益小

#### 4. 性能优化
**当前**: 顺序转换每个片段  
**潜在**: 并行转换多个片段 (使用 multiprocessing)

**优先级**: 中  
**理由**: 可能显著提升大量片段时的性能

**示例实现**:
```python
from concurrent.futures import ProcessPoolExecutor

def convert_segment(args):
    idx, segment_html, output_dir, original_name, options = args
    with NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(segment_html)
        tmp_path = Path(tmp_file.name)
    try:
        output_path = output_dir / f"{original_name}_page_{idx}.jpg"
        imgkit.from_file(str(tmp_path), str(output_path), options=options)
        return str(output_path)
    finally:
        tmp_path.unlink(missing_ok=True)

# 并行处理
with ProcessPoolExecutor() as executor:
    args_list = [(i, seg, output_dir, original_name, options) 
                  for i, seg in enumerate(html_segments)]
    generated_paths = list(executor.map(convert_segment, args_list))
```

#### 5. 嵌套 section 处理
**当前**: 不支持嵌套 section (按需求文档)  
**潜在**: 如果未来需要,可以添加嵌套 section 支持

**优先级**: 低  
**理由**: 当前 HTML 结构不使用嵌套 section

### 技术债务
**无**: 代码质量良好,测试完整,无技术债务
