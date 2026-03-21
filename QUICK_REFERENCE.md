# 视频分析快速参考卡

## 已完成的工作

✅ 从视频中提取了41个关键帧
✅ 生成交互式HTML查看器（已在浏览器中打开）
✅ 创建了完整的分析报告
✅ 提供了Python工具和脚本

## 文件位置速查

| 文件类型 | 位置 | 说明 |
|---------|------|------|
| 关键帧图像 | `D:\ClaudeWork\video_frames\` | 41张JPG图片 |
| HTML查看器 | `D:\ClaudeWork\video_frames\view_frames.html` | 网页形式查看所有帧 |
| 简明总结 | `D:\ClaudeWork\VIDEO_ANALYSIS_SUMMARY.md` | 本文档的详细版 |
| 完整报告 | `D:\ClaudeWork\video_analysis_report.md` | 技术细节和代码示例 |
| 工具指南 | `D:\ClaudeWork\VIDEO_ANALYSIS_TOOLS_GUIDE.md` | Python工具完整教程 |
| 提取脚本 | `D:\ClaudeWork\extract_frames_simple.py` | 简单版帧提取工具 |
| 完整脚本 | `D:\ClaudeWork\analyze_video.py` | 带OCR的完整分析工具 |

## 视频分析结果

### 视频内容
**Reddit手机App发帖演示** - 2分钟竖屏视频

### 发帖方法
使用Reddit官方移动应用的标准发帖功能：
1. 打开App
2. 创建帖子
3. 输入内容
4. 选择版块
5. 发布

**特点**: 常规操作，无特殊技巧

## 快速命令

### 查看关键帧
```bash
# 方法1: 打开HTML查看器（推荐）
start D:\ClaudeWork\video_frames\view_frames.html

# 方法2: 打开文件夹
explorer D:\ClaudeWork\video_frames
```

### 提取新视频的帧
```python
import cv2

video_path = "your_video.mp4"
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)

count = 0
while True:
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(count * fps * 3))
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imwrite(f"frame_{count}.jpg", frame)
    count += 1

cap.release()
```

### 安装推荐的Python工具
```bash
# 基础工具
pip install opencv-python numpy

# OCR文字识别（可选）
pip install easyocr          # 推荐
# 或
pip install pytesseract      # 需要安装Tesseract引擎

# 其他工具
pip install moviepy          # 视频编辑
pip install pillow           # 图像处理
```

## 自动化Reddit发帖

### 推荐方案: PRAW
```bash
pip install praw
```

```python
import praw

reddit = praw.Reddit(
    client_id="从reddit.com/prefs/apps获取",
    client_secret="从reddit.com/prefs/apps获取",
    user_agent="my_bot/1.0",
    username="你的用户名",
    password="你的密码"
)

# 发布帖子
subreddit = reddit.subreddit("目标版块")
submission = subreddit.submit(
    title="帖子标题",
    selftext="帖子内容"
)

print(f"发布成功! URL: {submission.url}")
```

### 获取API密钥
1. 访问 https://www.reddit.com/prefs/apps
2. 点击"create app"或"create another app"
3. 填写名称，选择"script"
4. 复制client_id和client_secret

## 常见问题

**Q: 如何查看提取的帧？**
A: 双击打开 `D:\ClaudeWork\video_frames\view_frames.html`

**Q: 如何分析其他视频？**
A: 修改 `extract_frames_simple.py` 中的视频路径，然后运行

**Q: OCR识别效果不好？**
A: 尝试使用easyocr代替pytesseract，效果更好

**Q: 如何自动化发帖？**
A: 使用PRAW库（Reddit官方API），不要用浏览器模拟

**Q: Reddit API有速率限制吗？**
A: 是的，具体限制取决于你的账号类型

## 视频信息

```
文件: RPReplay_Final1772232768.MP4
大小: 78 MB
分辨率: 886x1920 (竖屏)
帧率: 59.98 FPS
时长: 119.79 秒 (2分钟)
总帧数: 7185 帧
提取间隔: 每3秒一帧
提取数量: 41帧
```

## 技术栈

- **视频处理**: OpenCV
- **OCR**: EasyOCR / Tesseract
- **图像处理**: Pillow
- **Reddit API**: PRAW
- **开发语言**: Python 3.x

## 学习资源

- OpenCV文档: https://docs.opencv.org/
- PRAW文档: https://praw.readthedocs.io/
- Reddit API: https://www.reddit.com/dev/api/
- Python教程: 搜索"Python教程"

## 下一步

### 如果你想自动化发帖:
1. 学习PRAW库使用
2. 注册Reddit应用获取API密钥
3. 在r/test测试
4. 部署到服务器

### 如果你想分析更多视频:
1. 熟悉OpenCV基本操作
2. 尝试OCR文字识别
3. 学习场景检测算法

### 如果你想深入学习视频处理:
1. 学习FFmpeg命令行工具
2. 研究计算机视觉基础
3. 了解视频编码格式

---

**提示**: 所有脚本和文档都在 `D:\ClaudeWork\` 目录下
