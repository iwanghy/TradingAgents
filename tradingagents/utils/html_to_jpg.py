"""
HTML 到 JPG 转换工具模块

提供将 HTML 文件转换为 JPG 图片的功能，使用 imgkit 和 wkhtmltoimage。
"""

import shutil
from pathlib import Path
from typing import List
from tempfile import NamedTemporaryFile

import imgkit
from bs4 import BeautifulSoup, Comment


def check_wkhtmltoimage() -> bool:
    """检查 wkhtmltoimage 是否安装

    Returns:
        bool: 如果 wkhtmltoimage 已安装返回 True，否则返回 False
    """
    return shutil.which('wkhtmltoimage') is not None


def segment_html_by_sections(html_content: str) -> List[str]:
    """将 HTML 内容按主要部分分割成多个 HTML 片段

    支持两种分割策略:
    1. 按 container 直接子元素的 <h2> 标题分割
    2. 按 <div class="section"> 或 <section> 元素分割

    Args:
        html_content: 完整的 HTML 内容

    Returns:
        List[str]: 分割后的 HTML 片段列表
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取 style 标签
    style_tag = soup.find('style')
    
    # 提取原始 title
    title_tag = soup.find('title')
    title_text = title_tag.get_text() if title_tag else "分段报告"

    # 获取 container（主要内容区域）
    container = soup.find('div', class_='container')
    if not container:
        container = soup.find('body')

    if not container:
        return [html_content]

    # 构建 HTML 模板函数
    def build_html(content: str) -> str:
        style_str = str(style_tag) if style_tag else ""
        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_text}</title>
    {style_str}
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>'''

    # 辅助函数：检查节点是否应该被包含（排除注释）
    def should_include(child) -> bool:
        """检查节点是否应该被包含在输出中（排除 HTML 注释）"""
        if isinstance(child, Comment):
            return False
        if not str(child).strip():
            return False
        return True

    # 辅助函数：安全转换节点为字符串（排除注释）
    def child_to_str(child) -> str:
        """将节点转换为字符串，跳过注释"""
        if isinstance(child, Comment):
            return ''
        return str(child)

    # 策略 1: 检查是否有直接在 container 下的 h2 标签
    children = list(container.children)
    h2_positions = []
    for i, child in enumerate(children):
        if hasattr(child, 'name') and child.name == 'h2':
            h2_positions.append(i)

    segments = []

    if h2_positions:
        # 按 h2 标题分割
        # 第一个片段：header 到第一个 h2 之前（不包含 h2）
        first_content = ''.join(child_to_str(children[i]) for i in range(h2_positions[0]) if should_include(children[i]))
        if first_content:
            segments.append(build_html(first_content))

        # 每个 h2 片段：包含 h2 到下一个 h2 之前的元素
        # 但要排除下一个 h2 前面的纯文本节点（通常是注释）
        for idx, pos in enumerate(h2_positions):
            if idx < len(h2_positions) - 1:
                next_h2_pos = h2_positions[idx + 1]
                # 找到下一个有意义元素的位置（跳过纯文本节点）
                # 从 next_h2_pos - 1 向前找，直到找到有 name 的元素或到达 pos
                end_pos = next_h2_pos
                for j in range(next_h2_pos - 1, pos, -1):
                    child = children[j]
                    if hasattr(child, 'name') and child.name:
                        end_pos = j + 1
                        break
                    # 如果是纯文本节点（可能是注释），继续向前找
                content = ''.join(child_to_str(children[i]) for i in range(pos, end_pos))
            else:
                # 最后一个 h2：到 footer 之前
                footer_pos = len(children)
                for i in range(pos + 1, len(children)):
                    if hasattr(children[i], 'name') and children[i].name == 'footer':
                        footer_pos = i
                        break
                content = ''.join(child_to_str(children[i]) for i in range(pos, footer_pos))

            if content.strip():
                segments.append(build_html(content))

        # footer 单独一个片段
        footer = container.find('footer') or soup.find('footer')
        if footer:
            segments.append(build_html(str(footer)))

    else:
        # 策略 2: 按 section 元素分割
        sections = (
            container.find_all('div', class_='section') or
            container.find_all('section', class_='highlight-box') or
            container.find_all('section') or
            []
        )

        if not sections:
            content = ''.join(child_to_str(child) for child in children if should_include(child))
            return [build_html(content)]

        header = (
            container.find('div', class_='header') or
            container.find('header', class_='header-info') or
            container.find('header')
        )
        decision = (
            container.find('div', class_='decision') or
            container.find('div', class_='decision-card')
        )
        footer = (
            container.find('div', class_='footer') or
            container.find('footer', class_='disclaimer') or
            container.find('footer')
        )

        first_parts = []
        if header:
            first_parts.append(str(header))
        if decision:
            first_parts.append(str(decision))
        if sections:
            first_parts.append(str(sections[0]))

        if first_parts:
            segments.append(build_html(''.join(first_parts)))

        for i in range(1, len(sections)):
            segments.append(build_html(str(sections[i])))

        if footer:
            segments.append(build_html(str(footer)))

    return segments if segments else [html_content]


def convert(html_path: Path, output_dir: Path, quality: int = 85,
            enable_segmentation: bool = False, max_segments: int = 5) -> List[str]:
    """将 HTML 转换为 JPG 图片

    Args:
        html_path: HTML 文件路径
        output_dir: 输出目录路径
        quality: JPG 图片质量 (1-100)，默认 85
        enable_segmentation: 是否启用分段生成多张图片（暂未实现）
        max_segments: 最大分段数量（暂未实现）

    Returns:
        List[str]: 生成的 JPG 图片路径列表

    Raises:
        FileNotFoundError: 当 wkhtmltoimage 未安装或 HTML 文件不存在时
    """
    # 检查 wkhtmltoimage 是否安装
    if not check_wkhtmltoimage():
        raise FileNotFoundError(
            "wkhtmltoimage not found. Please install it: sudo apt-get install wkhtmltopdf"
        )

    # 检查 HTML 文件是否存在
    if not html_path.exists():
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取原始文件名（不带扩展名）
    original_name = html_path.stem

    # 配置 imgkit 选项
    options = {
        'format': 'jpg',
        'width': 750,
        'quality': quality,
        'encoding': 'UTF-8',
        'enable-local-file-access': ''
    }

    # 如果不启用分段，直接转换为单张图片
    if not enable_segmentation:
        output_path = output_dir / f"{original_name}_page_0.jpg"
        try:
            imgkit.from_file(str(html_path), str(output_path), options=options)
        except OSError as e:
            # imgkit 找不到 wkhtmltoimage 时抛出 OSError
            if "wkhtmltoimage" in str(e) or "command not found" in str(e):
                raise FileNotFoundError(
                    "wkhtmltoimage not found. Please install it: sudo apt-get install wkhtmltopdf"
                ) from e
            raise
        print(f"已生成: {output_path}")
        return [str(output_path)]

    # 启用分段功能
    # 读取原始 HTML 内容
    html_content = html_path.read_text(encoding='utf-8')

    # 分割 HTML 成多个片段
    html_segments = segment_html_by_sections(html_content)

    # 限制最大片段数量
    if len(html_segments) > max_segments:
        html_segments = html_segments[:max_segments]

    # 为每个片段生成对应的 JPG 图片
    generated_paths = []
    for idx, segment_html in enumerate(html_segments):
        # 创建临时 HTML 文件
        with NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp_file:
            tmp_file.write(segment_html)
            tmp_path = Path(tmp_file.name)

        try:
            # 生成输出文件路径
            output_path = output_dir / f"{original_name}_page_{idx}.jpg"

            # 转换为 JPG
            try:
                imgkit.from_file(str(tmp_path), str(output_path), options=options)
            except OSError as e:
                if "wkhtmltoimage" in str(e) or "command not found" in str(e):
                    raise FileNotFoundError(
                        "wkhtmltoimage not found. Please install it: sudo apt-get install wkhtmltopdf"
                    ) from e
                raise

            generated_paths.append(str(output_path))
            print(f"已生成: {output_path}")
        finally:
            # 清理临时文件
            tmp_path.unlink(missing_ok=True)

    return generated_paths
