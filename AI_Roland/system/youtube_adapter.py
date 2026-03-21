"""
AI Roland YouTube 适配器
集成 yt-search-download Skill，提供统一的 YouTube 操作接口
"""

import subprocess
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class YouTubeAdapter:
    """YouTube 适配器 - 统一 YouTube 搜索、下载、字幕提取"""

    def __init__(self):
        # Skill 安装路径
        self.skill_path = Path.home() / ".agents" / "skills" / "yt-search-download"
        self.script_path = self.skill_path / "scripts" / "yt_search.py"
        self.yt_dlp_path = Path("C:\\Users\\DELL\\AppData\\Local\\Programs\\Python\\Python314\\Scripts\\yt-dlp.exe")

        # 检查安装
        self._check_installation()

    def _check_installation(self) -> bool:
        """检查依赖是否安装"""
        if not self.script_path.exists():
            raise FileNotFoundError(f"yt-search-download Skill 未找到: {self.script_path}")

        if not self.yt_dlp_path.exists():
            # 尝试在系统 PATH 中查找
            import shutil
            yt_dlp = shutil.which("yt-dlp")
            if not yt_dlp:
                raise FileNotFoundError("yt-dlp 未安装，请运行: pip install yt-dlp")
            self.yt_dlp_path = Path(yt_dlp)

        return True

    def _run_script(self, args: List[str]) -> str:
        """运行 yt_search.py 脚本"""
        cmd = ["python", str(self.script_path)] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout

    def search(
        self,
        query: str,
        count: int = 20,
        order: str = "relevance",
        after: Optional[str] = None,
        before: Optional[str] = None,
        channel: Optional[str] = None,
        json_output: bool = True
    ) -> List[Dict[str, Any]]:
        """
        全站关键词搜索

        Args:
            query: 搜索关键词
            count: 返回数量（默认 20）
            order: 排序方式 (relevance/date/viewCount)
            after: 发布时间起 (YYYY-MM-DD)
            before: 发布时间止 (YYYY-MM-DD)
            channel: 限定频道 (@handle)
            json_output: JSON 格式输出

        Returns:
            视频列表（包含标题、URL、时长、播放量等）
        """
        args = ["search", query, "-n", str(count)]

        if order != "relevance":
            args.extend(["-o", order])

        if after:
            args.extend(["--after", after])

        if before:
            args.extend(["--before", before])

        if channel:
            args.extend(["-c", channel])

        if json_output:
            args.append("--json")

        output = self._run_script(args)

        if json_output:
            try:
                # 尝试解析 JSON
                for line in output.split('\n'):
                    if line.strip().startswith('{'):
                        return json.loads(line)
            except json.JSONDecodeError:
                pass

        # 如果不是 JSON 或解析失败，返回原始输出
        return {"raw": output}

    def channel(
        self,
        handle: str,
        count: int = 10,
        query: Optional[str] = None,
        order: str = "date",
        min_duration: Optional[str] = None,
        max_duration: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        浏览频道视频

        Args:
            handle: 频道 (@handle 或 URL)
            count: 返回数量
            query: 频道内搜索关键词
            order: 排序方式
            min_duration: 最短时长 (如 "30m", "1h")
            max_duration: 最长时长

        Returns:
            视频列表
        """
        args = ["channel", handle, "-n", str(count)]

        if query:
            args.extend(["-q", query])

        if order != "date":
            args.extend(["-o", order])

        if min_duration:
            args.extend(["--min-duration", min_duration])

        if max_duration:
            args.extend(["--max-duration", max_duration])

        args.append("--json")

        output = self._run_script(args)

        try:
            for line in output.split('\n'):
                if line.strip().startswith('{'):
                    return json.loads(line)
        except json.JSONDecodeError:
            pass

        return {"raw": output}

    def download(
        self,
        url: str,
        quality: Optional[str] = None,
        directory: Optional[Path] = None,
        audio_only: bool = False
    ) -> Dict[str, Any]:
        """
        下载视频/音频

        Args:
            url: 视频 URL
            quality: 画质 (1080p, 720p, etc.)
            directory: 保存目录
            audio_only: 仅下载音频

        Returns:
            下载结果
        """
        args = ["download", url]

        if quality:
            args.extend(["-q", quality])

        if directory:
            args.extend(["--dir", str(directory)])

        if audio_only:
            args.append("--audio-only")

        output = self._run_script(args)

        return {"success": True, "output": output, "path": str(directory or " Downloads")}

    def get_info(self, url: str) -> Dict[str, Any]:
        """
        获取视频详情

        Args:
            url: 视频 URL

        Returns:
            视频信息（标题、时长、播放量等）
        """
        args = ["info", url]
        output = self._run_script(args)

        # 解析输出
        info = {}

        # 提取标题
        title_match = re.search(r'Title:\s*(.+)', output)
        if title_match:
            info['title'] = title_match.group(1).strip()

        # 提取时长
        duration_match = re.search(r'Duration:\s*(.+)', output)
        if duration_match:
            info['duration'] = duration_match.group(1).strip()

        # 提取播放量
        views_match = re.search(r'Views:\s*(.+)', output)
        if views_match:
            info['views'] = views_match.group(1).strip()

        return info

    def download_subtitles(
        self,
        url: str,
        lang: str = "en",
        output_dir: Optional[Path] = None,
        generate_txt: bool = True
    ) -> Dict[str, Path]:
        """
        下载字幕（SRT + TXT）

        Args:
            url: 视频 URL
            lang: 字幕语言 (en, zh-Hans)
            output_dir: 输出目录
            generate_txt: 是否生成 TXT 文件

        Returns:
            {"srt": Path, "txt": Path}
        """
        if output_dir is None:
            output_dir = Path.home() / "Downloads"

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 获取视频标题用于文件名
        info = self.get_info(url)
        title = info.get('title', 'video').replace('/', '_').replace('\\', '_')[:50]

        # 构建 yt-dlp 命令
        cmd = [
            str(self.yt_dlp_path),
            "--cookies-from-browser", "chrome",
            "--write-auto-sub", "--write-sub",
            "--sub-lang", lang,
            "--convert-subs", "srt",
            "--skip-download",
            "-o", str(output_dir / f"{title}.%(ext)s"),
            url
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        srt_file = output_dir / f"{title}.{lang}.srt"

        if not srt_file.exists():
            # 尝试自动字幕
            srt_file = output_dir / f"{title}.{lang}.auto.srt"

        result_dict = {"srt": srt_file if srt_file.exists() else None}

        # 生成 TXT 文件
        if generate_txt and srt_file.exists():
            txt_file = self._srt_to_txt(srt_file)
            result_dict["txt"] = txt_file

        return result_dict

    def _srt_to_txt(self, srt_path: Path) -> Path:
        """将 SRT 转换为 TXT（保留时间戳）"""
        txt_path = srt_path.with_suffix('.txt')

        with open(srt_path, 'r', encoding='utf-8') as f:
            srt_content = f.read()

        # 去除序号行，保留时间戳和文本
        txt_content = re.sub(r'^\d+\s*\n', '', srt_content, flags=re.MULTILINE)
        txt_content = re.sub(r'\n{3,}', '\n\n', txt_content).strip()

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)

        return txt_path

    def format_results(self, results: List[Dict], translate: bool = True) -> str:
        """
        格式化搜索结果为 Markdown 表格

        Args:
            results: 搜索结果
            translate: 是否翻译标题

        Returns:
            Markdown 格式的表格
        """
        if isinstance(results, dict) and "raw" in results:
            return results["raw"]

        lines = []
        lines.append("| # | 标题 | 日期 | 时长 | 播放量 |")
        lines.append("|---|---|---|---|---|")

        for i, video in enumerate(results.get('videos', []), 1):
            title = video.get('title', 'N/A')
            url = video.get('url', '')
            date = video.get('published_at', 'N/A')
            duration = video.get('duration', 'N/A')
            views = video.get('view_count', 'N/A')

            # 格式化标题（带链接）
            formatted_title = f"[{title}]({url})"

            lines.append(f"| {i} | {formatted_title} | {date} | {duration} | {views} |")

        return "\n".join(lines)


# 单例实例
_youtube_adapter: Optional[YouTubeAdapter] = None


def get_youtube_adapter() -> YouTubeAdapter:
    """获取 YouTube 适配器单例"""
    global _youtube_adapter
    if _youtube_adapter is None:
        _youtube_adapter = YouTubeAdapter()
    return _youtube_adapter


if __name__ == "__main__":
    import sys
    import io

    # 设置 UTF-8 输出
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    # 测试
    yt = get_youtube_adapter()

    # 测试搜索
    print("测试搜索...")
    results = yt.search("AI agent", count=5)
    print(yt.format_results(results))
