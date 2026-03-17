# HTML to JPG Converter - 学习笔记

## 2026-03-17 - 章节分割功能实现

### 成功模式

#### 1. HTML 分割策略
- 使用 BeautifulSoup 解析 HTML,提取关键元素
- 第一个片段: header + decision + 第一个 section (如果有)
- 中间片段: 剩余的 sections (除了第一个和最后一个)
- 最后一个片段: 最后一个 section + footer (或仅 footer)

#### 2. 临时文件处理
- 使用 `NamedTemporaryFile` 创建临时 HTML 文件
- 在 `finally` 块中确保清理临时文件: `tmp_path.unlink(missing_ok=True)`
- 避免临时文件泄漏

#### 3. 图片生成
- 使用 imgkit.from_file() 转换每个 HTML 片段
- 文件命名: `{original}_page_{idx}.jpg`
- 返回所有生成的图片路径列表

#### 4. 错误处理
- 验证 HTML 结构完整性 (header, decision, footer 必须存在)
- 处理 imgkit OSError 转换为 FileNotFoundError
- 提供清晰的错误消息

### 关键实现细节

#### BeautifulSoup 元素提取
```python
soup = BeautifulSoup(html_content, 'html.parser')
header = soup.find('div', class_='header')
sections = soup.find_all('div', class_='section')
```

#### HTML 片段构建
```python
def build_html(content: str) -> str:
    style_str = str(style_tag) if style_tag else ""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <style>{style_str}</style>
</head>
<body>
    <div class="container">{content}</div>
</body>
</html>'''
```

### 测试验证
- 所有测试通过 (4/4)
- `test_segmentation` 验证多图生成、文件命名、格式正确性
- 保持向后兼容性 (`enable_segmentation=False` 时行为不变)

