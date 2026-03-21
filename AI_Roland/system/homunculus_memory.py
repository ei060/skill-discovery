"""
AI Roland Homunculus Memory System
整合 ECC v2.1 Homunculus 学习机制与 AI Roland 记忆树系统

特性:
1. Hook 观察捕获 (ECC) - 100% 可靠
2. 项目作用域本能 (ECC)
3. 生命周期管理 (AI Roland)
4. 精华提取与复苏 (AI Roland)
5. 本能进化 (ECC)
6. 项目到全局提升 (ECC)
"""

import sys
import os
import json
import hashlib
import subprocess
import uuid
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from collections import defaultdict
from dataclasses import dataclass, field, asdict

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'

# ─────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────

class Config:
    """统一配置系统"""

    # 目录配置
    WORKSPACE = Path(__file__).parent.parent
    SYSTEM_DIR = WORKSPACE / "system"
    HOMUNCULUS_DIR = SYSTEM_DIR / "homunculus"
    PROJECTS_DIR = HOMUNCULUS_DIR / "projects"

    # 全局路径
    GLOBAL_INSTINCTS_DIR = HOMUNCULUS_DIR / "instincts"
    GLOBAL_PERSONAL_DIR = GLOBAL_INSTINCTS_DIR / "personal"
    GLOBAL_INHERITED_DIR = GLOBAL_INSTINCTS_DIR / "inherited"
    GLOBAL_EVOLVED_DIR = HOMUNCULUS_DIR / "evolved"
    GLOBAL_OBSERVATIONS_FILE = HOMUNCULUS_DIR / "observations.jsonl"

    # 生命周期阈值 (基于 AI Roland 记忆树)
    CONFIDENCE_SPROUT = 0.7      # 萌芽
    CONFIDENCE_GREEN = 0.8       # 绿叶
    CONFIDENCE_YELLOW_LOW = 0.5  # 黄叶
    CONFIDENCE_WITHERED = 0.3    # 枯叶
    CONFIDENCE_SOIL = 0.0        # 土壤

    # 优先级定义
    PRIORITY_P0 = "P0"  # 核心知识，永不衰减
    PRIORITY_P1 = "P1"  # 重要知识，缓慢衰减
    PRIORITY_P2 = "P2"  # 普通知识，正常衰减

    # 置信度变化值
    BOOST_SEARCH = 0.03       # 搜索命中
    BOOST_USE = 0.08         # 引用使用
    BOOST_IMPORTANT = 0.95   # 人工标记重要
    BOOST_OBSERVATION = 0.05 # 观察确认

    DECAY_P2_DAILY = 0.008   # P2 每天衰减
    DECAY_P1_DAILY = 0.004   # P1 每天衰减
    DECAY_P0_DAILY = 0.0     # P0 不衰减

    # 提升阈值 (ECC)
    PROMOTE_CONFIDENCE_THRESHOLD = 0.8
    PROMOTE_MIN_PROJECTS = 2

    # 观察配置
    MAX_OBSERVATIONS_FILE_SIZE_MB = 10
    OBSERVATIONS_ARCHIVE_DAYS = 30


# ─────────────────────────────────────────────
# 数据模型
# ─────────────────────────────────────────────

@dataclass
class Instinct:
    """本能数据模型 (ECC 风格 + AI Roland 生命周期)"""
    id: str
    trigger: str
    confidence: float = 0.7
    domain: str = "general"
    source: str = "session-observation"
    scope: str = "project"  # project | global

    # 项目上下文
    project_id: str = "global"
    project_name: str = "global"

    # AI Roland 生命周期扩展
    lifecycle_stage: str = "sprout"  # sprout | green | yellow | withered | soil
    priority: str = Config.PRIORITY_P2

    # 内容
    action: str = ""
    evidence: List[str] = field(default_factory=list)

    # 元数据
    created_at: str = ""
    last_updated: str = ""
    last_accessed: str = ""
    access_count: int = 0
    observation_count: int = 0

    # 来源追踪
    parent_soil_id: Optional[str] = None
    imported_from: Optional[str] = None
    source_repo: Optional[str] = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        if not self.last_updated:
            self.last_updated = self.created_at
        if not self.last_accessed:
            self.last_accessed = self.created_at
        self._update_lifecycle_stage()

    def _update_lifecycle_stage(self):
        """根据置信度更新生命周期阶段"""
        if self.confidence >= Config.CONFIDENCE_GREEN:
            self.lifecycle_stage = "green"
        elif self.confidence >= Config.CONFIDENCE_YELLOW_LOW:
            self.lifecycle_stage = "yellow"
        elif self.confidence > Config.CONFIDENCE_WITHERED:
            self.lifecycle_stage = "sprout"
        else:
            self.lifecycle_stage = "withered"

    def get_status_icon(self) -> str:
        """获取状态图标"""
        icons = {
            "sprout": "🌱",
            "green": "🌿",
            "yellow": "🍂",
            "withered": "🍁",
            "soil": "🪨"
        }
        return icons.get(self.lifecycle_stage, "📄")

    def to_yaml(self) -> str:
        """导出为 YAML 格式"""
        lines = ["---"]
        lines.extend([
            f"id: {self.id}",
            f"trigger: \"{self.trigger}\"",
            f"confidence: {self.confidence}",
            f"domain: {self.domain}",
            f"source: {self.source}",
            f"scope: {self.scope}",
            f"lifecycle_stage: {self.lifecycle_stage}",
            f"priority: {self.priority}",
        ])

        if self.scope == "project":
            lines.extend([
                f"project_id: {self.project_id}",
                f"project_name: {self.project_name}",
            ])

        if self.parent_soil_id:
            lines.append(f"parent_soil_id: {self.parent_soil_id}")
        if self.imported_from:
            lines.append(f"imported_from: \"{self.imported_from}\"")
        if self.source_repo:
            lines.append(f"source_repo: {self.source_repo}")

        lines.extend([
            f"created_at: {self.created_at}",
            f"last_updated: {self.last_updated}",
            f"access_count: {self.access_count}",
            f"observation_count: {self.observation_count}",
            "---",
            "",
            f"# {self.id}",
            "",
            "## Action",
            self.action,
            ""
        ])

        if self.evidence:
            lines.append("## Evidence")
            for ev in self.evidence:
                lines.append(f"- {ev}")
            lines.append("")

        return "\n".join(lines)

    @classmethod
    def from_yaml(cls, content: str) -> 'Instinct':
        """从 YAML 解析"""
        parsed = cls._parse_yaml_frontmatter(content)
        body = content.split("---", 2)[-1] if "---" in content else content

        # 提取 action
        action = ""
        action_match = re.search(r'## Action\s*\n\s*(.+?)(?:\n\n|\n##|$)', body, re.DOTALL)
        if action_match:
            action = action_match.group(1).strip()

        # 提取 evidence
        evidence = []
        evidence_match = re.search(r'## Evidence\s*\n(.+?)(?:\n\n|\n##|$)', body, re.DOTALL)
        if evidence_match:
            for line in evidence_match.group(1).strip().split('\n'):
                line = line.strip()
                if line.startswith(('-', '*', '•')):
                    evidence.append(line.lstrip('-*• ').strip())

        return cls(
            id=parsed.get('id', ''),
            trigger=parsed.get('trigger', ''),
            confidence=float(parsed.get('confidence', 0.7)),
            domain=parsed.get('domain', 'general'),
            source=parsed.get('source', 'session-observation'),
            scope=parsed.get('scope', 'project'),
            project_id=parsed.get('project_id', 'global'),
            project_name=parsed.get('project_name', 'global'),
            lifecycle_stage=parsed.get('lifecycle_stage', 'sprout'),
            priority=parsed.get('priority', Config.PRIORITY_P2),
            action=action,
            evidence=evidence,
            parent_soil_id=parsed.get('parent_soil_id'),
            imported_from=parsed.get('imported_from'),
            source_repo=parsed.get('source_repo'),
            created_at=parsed.get('created_at', ''),
            last_updated=parsed.get('last_updated', ''),
            access_count=int(parsed.get('access_count', 0)),
            observation_count=int(parsed.get('observation_count', 0)),
        )

    @staticmethod
    def _parse_yaml_frontmatter(content: str) -> Dict:
        """解析 YAML frontmatter"""
        result = {}
        in_frontmatter = False

        for line in content.split('\n'):
            line = line.strip()
            if line == '---':
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter and ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip().strip('"').strip("'")

        return result


@dataclass
class Observation:
    """观察记录"""
    timestamp: str
    event: str  # tool_start | tool_complete
    tool: str
    session: str
    project_id: str = "global"
    project_name: str = "global"
    input: Optional[str] = None
    output: Optional[str] = None
    cwd: Optional[str] = None
    tool_use_id: str = ""

    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp,
            "event": self.event,
            "tool": self.tool,
            "session": self.session,
            "project_id": self.project_id,
            "project_name": self.project_name,
            "input": self.input,
            "output": self.output,
            "cwd": self.cwd,
            "tool_use_id": self.tool_use_id,
        })


# ─────────────────────────────────────────────
# 项目检测
# ─────────────────────────────────────────────

def detect_project(workspace: Path = None) -> Dict:
    """检测当前项目上下文"""
    if workspace is None:
        workspace = Config.WORKSPACE

    project_root = None

    # 1. CLAUDE_PROJECT_DIR env var
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir and os.path.isdir(env_dir):
        project_root = env_dir

    # 2. git repo root
    if not project_root:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=5,
                cwd=workspace
            )
            if result.returncode == 0:
                project_root = result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

    # 3. 全局回退
    if not project_root:
        return {
            "id": "global",
            "name": "global",
            "root": "",
            "project_dir": Config.HOMUNCULUS_DIR,
            "instincts_personal": Config.GLOBAL_PERSONAL_DIR,
            "instincts_inherited": Config.GLOBAL_INHERITED_DIR,
            "evolved_dir": Config.GLOBAL_EVOLVED_DIR,
            "observations_file": Config.GLOBAL_OBSERVATIONS_FILE,
        }

    project_name = os.path.basename(project_root)

    # 从 git remote URL 或路径获取项目 ID
    remote_url = ""
    try:
        result = subprocess.run(
            ["git", "-C", project_root, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            remote_url = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    hash_source = remote_url if remote_url else project_root
    project_id = hashlib.sha256(hash_source.encode()).hexdigest()[:12]

    project_dir = Config.PROJECTS_DIR / project_id

    # 确保项目目录结构
    for d in [
        project_dir / "instincts" / "personal",
        project_dir / "instincts" / "inherited",
        project_dir / "observations.archive",
        project_dir / "evolved" / "skills",
        project_dir / "evolved" / "commands",
        project_dir / "evolved" / "agents",
        project_dir / "soil",  # AI Roland 土壤存储
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # 更新注册表
    _update_registry(project_id, project_name, project_root, remote_url)

    return {
        "id": project_id,
        "name": project_name,
        "root": project_root,
        "remote": remote_url,
        "project_dir": project_dir,
        "instincts_personal": project_dir / "instincts" / "personal",
        "instincts_inherited": project_dir / "instincts" / "inherited",
        "evolved_dir": project_dir / "evolved",
        "soil_dir": project_dir / "soil",
        "observations_file": project_dir / "observations.jsonl",
    }


def _update_registry(pid: str, pname: str, proot: str, premote: str) -> None:
    """更新项目注册表"""
    registry_file = Config.HOMUNCULUS_DIR / "projects.json"

    try:
        with open(registry_file, encoding="utf-8") as f:
            registry = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        registry = {}

    registry[pid] = {
        "name": pname,
        "root": proot,
        "remote": premote,
        "last_seen": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    registry_file.parent.mkdir(parents=True, exist_ok=True)
    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)


def load_registry() -> dict:
    """加载项目注册表"""
    registry_file = Config.HOMUNCULUS_DIR / "projects.json"
    try:
        with open(registry_file, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


# ─────────────────────────────────────────────
# 核心记忆系统
# ─────────────────────────────────────────────

class HomunculusMemory:
    """
    统一记忆系统 - 整合 ECC Homunculus 与 AI Roland 记忆树
    """

    def __init__(self, workspace: Path = None):
        # 确保目录存在
        for d in [
            Config.HOMUNCULUS_DIR,
            Config.PROJECTS_DIR,
            Config.GLOBAL_PERSONAL_DIR,
            Config.GLOBAL_INHERITED_DIR,
            Config.GLOBAL_EVOLVED_DIR / "skills",
            Config.GLOBAL_EVOLVED_DIR / "commands",
            Config.GLOBAL_EVOLVED_DIR / "agents",
        ]:
            d.mkdir(parents=True, exist_ok=True)

        # 检测项目
        self.project = detect_project(workspace)

        # 数据存储
        self.instincts: Dict[str, Instinct] = {}
        self.soil: Dict[str, Dict] = {}  # AI Roland 土壤存储

        # 统计数据
        self.stats = {
            "total_instincts": 0,
            "sprouts": 0,
            "green_leaves": 0,
            "yellow_leaves": 0,
            "withered_leaves": 0,
            "soil_count": 0,
            "project_scoped": 0,
            "global_scoped": 0,
        }

        # 加载现有数据
        self._load_all()
        self._update_stats()

    def _load_all(self):
        """加载所有本能和土壤数据"""
        # 加载项目本能
        if self.project["id"] != "global":
            self._load_instincts_from_dir(self.project["instincts_personal"], "project")
            self._load_instincts_from_dir(self.project["instincts_inherited"], "project")

        # 加载全局本能
        self._load_instincts_from_dir(Config.GLOBAL_PERSONAL_DIR, "global")
        self._load_instincts_from_dir(Config.GLOBAL_INHERITED_DIR, "global")

        # 加载土壤
        self._load_soil()

    def _load_instincts_from_dir(self, directory: Path, scope_label: str):
        """从目录加载本能"""
        if not directory.exists():
            return

        for file in directory.iterdir():
            if not file.is_file() or file.suffix.lower() not in {".yaml", ".yml", ".md"}:
                continue

            try:
                content = file.read_text(encoding="utf-8")
                instinct = Instinct.from_yaml(content)

                # 项目作用域本能优先于全局
                if instinct.id not in self.instincts:
                    self.instincts[instinct.id] = instinct
            except Exception as e:
                print(f"[WARNING] 加载本能失败 {file}: {e}")

    def _load_soil(self):
        """加载土壤数据"""
        soil_file = self.project.get("soil_dir", Config.HOMUNCULUS_DIR / "soil") / "soil_db.json"

        if soil_file.exists():
            try:
                with open(soil_file, encoding="utf-8") as f:
                    self.soil = json.load(f)
            except Exception:
                self.soil = {}

    def _save_soil(self):
        """保存土壤数据"""
        soil_dir = self.project.get("soil_dir", Config.HOMUNCULUS_DIR / "soil")
        soil_dir.mkdir(parents=True, exist_ok=True)

        soil_file = soil_dir / "soil_db.json"
        with open(soil_file, "w", encoding="utf-8") as f:
            json.dump(self.soil, f, indent=2, ensure_ascii=False)

    def add_instinct(self,
                     id: str,
                     trigger: str,
                     action: str,
                     confidence: float = 0.7,
                     domain: str = "general",
                     scope: str = "project",
                     evidence: List[str] = None,
                     priority: str = None) -> Instinct:
        """添加新本能"""
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        instinct = Instinct(
            id=id,
            trigger=trigger,
            action=action,
            confidence=confidence,
            domain=domain,
            source="session-observation",
            scope=scope,
            project_id=self.project["id"],
            project_name=self.project["name"],
            lifecycle_stage="sprout",
            priority=priority if priority else Config.PRIORITY_P2,
            evidence=evidence or [],
            created_at=now,
            last_updated=now,
            last_accessed=now,
        )

        # 保存到文件
        self._save_instinct(instinct)

        # 更新内存
        self.instincts[id] = instinct
        self._update_stats()

        return instinct

    def _save_instinct(self, instinct: Instinct):
        """保存本能到文件"""
        # 确定目标目录
        if instinct.scope == "global":
            output_dir = Config.GLOBAL_PERSONAL_DIR
        else:
            output_dir = self.project["instincts_personal"]

        output_dir.mkdir(parents=True, exist_ok=True)

        # 写入文件
        output_file = output_dir / f"{instinct.id}.yaml"
        output_file.write_text(instinct.to_yaml(), encoding="utf-8")

    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """搜索本能"""
        results = []
        query_lower = query.lower()

        for iid, instinct in self.instincts.items():
            # 跳过已归档的
            if instinct.lifecycle_stage == "soil":
                continue

            score = 0

            # 标题匹配
            if query_lower in instinct.id.lower():
                score += 10

            # 触发器匹配
            if query_lower in instinct.trigger.lower():
                score += 8

            # 动作匹配
            if query_lower in instinct.action.lower():
                score += 5

            # 域名匹配
            if query_lower in instinct.domain.lower():
                score += 3

            if score > 0:
                # 置信度加成
                score = score * (1 + instinct.confidence)
                results.append({
                    "instinct_id": iid,
                    "score": score,
                    "confidence": instinct.confidence,
                    "lifecycle_stage": instinct.lifecycle_stage,
                    "instinct": instinct,
                })

        # 排序
        results.sort(key=lambda x: x["score"], reverse=True)

        # 提升命中本能的置信度 (AI Roland 特性)
        for result in results[:top_k]:
            self._boost_confidence(result["instinct_id"], Config.BOOST_SEARCH, "search")
            self.instincts[result["instinct_id"]].last_accessed = datetime.now(
                timezone.utc).isoformat().replace("+00:00", "Z")
            self.instincts[result["instinct_id"]].access_count += 1

        self._save_dirty()

        return results[:top_k]

    def use_instinct(self, instinct_id: str) -> bool:
        """使用本能（大幅提升置信度）"""
        if instinct_id not in self.instincts:
            return False

        instinct = self.instincts[instinct_id]
        if instinct.lifecycle_stage == "soil":
            return False

        self._boost_confidence(instinct_id, Config.BOOST_USE, "use")
        instinct.last_accessed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        instinct.access_count += 1

        self._save_instinct(instinct)
        self._update_stats()

        return True

    def mark_important(self, instinct_id: str) -> bool:
        """标记为重要（提升到高置信度和 P0 优先级）"""
        if instinct_id not in self.instincts:
            return False

        instinct = self.instincts[instinct_id]
        self._boost_confidence(instinct_id, Config.BOOST_IMPORTANT, "manual")
        instinct.priority = Config.PRIORITY_P0

        self._save_instinct(instinct)
        self._update_stats()

        return True

    def update_instinct(self, instinct_id: str, **kwargs) -> bool:
        """更新本能属性

        Args:
            instinct_id: 本能ID
            **kwargs: 要更新的属性 (confidence, lifecycle_stage, scope, etc.)

        Returns:
            是否成功
        """
        if instinct_id not in self.instincts:
            return False

        instinct = self.instincts[instinct_id]

        # 更新属性
        for key, value in kwargs.items():
            if hasattr(instinct, key):
                setattr(instinct, key, value)

        # 如果更新了置信度，触发生命周期更新
        if 'confidence' in kwargs:
            instinct._update_lifecycle_stage()

        instinct.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        self._save_instinct(instinct)
        self._update_stats()

        return True

    def promote_to_global(self, instinct_id: str) -> bool:
        """将项目本能提升为全局本能

        Args:
            instinct_id: 本能ID

        Returns:
            是否成功
        """
        if instinct_id not in self.instincts:
            return False

        instinct = self.instincts[instinct_id]

        # 检查是否已经是全局
        if instinct.scope == "global":
            return True

        # 检查置信度是否足够
        if instinct.confidence < Config.PROMOTE_CONFIDENCE_THRESHOLD:
            return False

        # 更新作用域
        old_scope = instinct.scope
        instinct.scope = "global"
        instinct.project_id = "global"
        instinct.project_name = "global"
        instinct.source = "promoted-from-project"
        instinct.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # 移动文件到全局目录
        old_file = self.project.get("instincts_personal", Config.GLOBAL_PERSONAL_DIR) / f"{instinct_id}.json"
        new_file = Config.GLOBAL_PERSONAL_DIR / f"{instinct_id}.json"

        if old_file.exists():
            import shutil
            new_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_file), str(new_file))

        self._save_instinct(instinct)
        self._update_stats()

        return True

    def get_instinct(self, instinct_id: str) -> Optional[Instinct]:
        """获取指定本能

        Args:
            instinct_id: 本能ID

        Returns:
            本能对象或None
        """
        return self.instincts.get(instinct_id)

    def _boost_confidence(self, instinct_id: str, boost_amount: float, reason: str):
        """提升置信度"""
        instinct = self.instincts[instinct_id]

        if boost_amount >= 1.0:
            # 直接设置
            new_value = boost_amount
        else:
            # 累加
            new_value = min(1.0, instinct.confidence + boost_amount)

        instinct.confidence = new_value
        instinct.last_updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # 更新生命周期阶段
        instinct._update_lifecycle_stage()

        # 更新历史记录
        if not hasattr(instinct, 'confidence_history'):
            instinct.confidence_history = []
        instinct.confidence_history.append({
            "action": reason,
            "old_value": instinct.confidence,
            "new_value": new_value,
            "timestamp": instinct.last_updated,
        })

    def _save_dirty(self):
        """保存已修改的本能"""
        for instinct in self.instincts.values():
            # 简化处理：保存所有非土壤本能
            if instinct.lifecycle_stage != "soil":
                self._save_instinct(instinct)

    def _update_stats(self):
        """更新统计数据"""
        self.stats = {
            "total_instincts": 0,
            "sprouts": 0,
            "green_leaves": 0,
            "yellow_leaves": 0,
            "withered_leaves": 0,
            "soil_count": len(self.soil),
            "project_scoped": 0,
            "global_scoped": 0,
        }

        for instinct in self.instincts.values():
            if instinct.lifecycle_stage != "soil":
                self.stats["total_instincts"] += 1

                # 生命周期统计
                stage = instinct.lifecycle_stage
                if stage == "sprout":
                    self.stats["sprouts"] += 1
                elif stage == "green":
                    self.stats["green_leaves"] += 1
                elif stage == "yellow":
                    self.stats["yellow_leaves"] += 1
                elif stage == "withered":
                    self.stats["withered_leaves"] += 1

                # 作用域统计
                if instinct.scope == "project":
                    self.stats["project_scoped"] += 1
                else:
                    self.stats["global_scoped"] += 1

    def get_status_report(self) -> str:
        """获取状态报告"""
        self._update_stats()

        lines = []
        lines.append("╔════════════════════════════════════════════════════════════╗")
        lines.append("║            🧠 Homunculus Memory System                   ║")
        lines.append("║        ECC v2.1 + AI Roland 记忆树整合                   ║")
        lines.append("╚════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"📊 当前项目: {self.project['name']} ({self.project['id']})")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        # 生命周期状态
        lines.append("🌱 生命周期状态")
        lines.append(f"  🌱 萌芽: {self.stats['sprouts']} 个")
        lines.append(f"  🌿 绿叶: {self.stats['green_leaves']} 个")
        lines.append(f"  🍂 黄叶: {self.stats['yellow_leaves']} 个")
        lines.append(f"  🍁 枯叶: {self.stats['withered_leaves']} 个")
        lines.append(f"  🪨 土壤: {self.stats['soil_count']} 份精华")
        lines.append(f"  ─────────────────────────────────────")
        lines.append(f"  总计: {self.stats['total_instincts']} 个本能")
        lines.append("")

        # 作用域统计
        lines.append("📁 作用域分布")
        lines.append(f"  项目作用域: {self.stats['project_scoped']} 个")
        lines.append(f"  全局作用域: {self.stats['global_scoped']} 个")
        lines.append("")

        # 健康度
        if self.stats['total_instincts'] > 0:
            health_ratio = self.stats['green_leaves'] / self.stats['total_instincts']
            lines.append(f"💚 记忆树健康度: {health_ratio:.1%}")
            if health_ratio > 0.6:
                lines.append("   状态: 茂盛 🌳")
            elif health_ratio > 0.3:
                lines.append("   状态: 健康 🌿")
            else:
                lines.append("   状态: 需要关注 🍂")
        lines.append("")

        # 最近活动
        lines.append("🕐 最近访问的本能")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        recent = sorted(
            [(k, v) for k, v in self.instincts.items()],
            key=lambda x: x[1].last_accessed,
            reverse=True
        )[:5]

        for iid, instinct in recent:
            lines.append(f"  {instinct.get_status_icon()} {instinct.id} "
                        f"({instinct.confidence:.2f}) [{instinct.scope}]")

        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(lines)

    def add_observation(self, observation: Observation):
        """添加观察记录"""
        obs_file = self.project["observations_file"]

        # 归档大文件
        if obs_file.exists():
            size_mb = obs_file.stat().st_size / (1024 * 1024)
            if size_mb >= Config.MAX_OBSERVATIONS_FILE_SIZE_MB:
                archive_dir = self.project["project_dir"] / "observations.archive"
                archive_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                obs_file.rename(archive_dir / f"observations-{timestamp}.jsonl")

        # 追加新观察
        with open(obs_file, "a", encoding="utf-8") as f:
            f.write(observation.to_json() + "\n")

    def get_observations(self, limit: int = 100) -> List[Dict]:
        """获取最近的观察记录"""
        obs_file = self.project["observations_file"]
        if not obs_file.exists():
            return []

        observations = []
        with open(obs_file, encoding="utf-8") as f:
            for line in f:
                try:
                    observations.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        return observations[-limit:]

    def analyze_observations(self) -> List[Instinct]:
        """
        分析观察记录，检测模式并创建本能
        简化版：检测重复的工具使用模式
        """
        observations = self.get_observations(200)

        if len(observations) < 10:
            return []

        # 统计工具使用模式
        tool_patterns = defaultdict(lambda: {"count": 0, "sessions": set()})

        for obs in observations:
            if obs["event"] == "tool_start":
                key = f"{obs['tool']}"
                tool_patterns[key]["count"] += 1
                tool_patterns[key]["sessions"].add(obs["session"])

        # 检测模式
        new_instincts = []

        for pattern, data in tool_patterns.items():
            if data["count"] >= 5:  # 至少5次观察
                instinct_id = f"use-{pattern.lower().replace('_', '-')}"

                # 跳过已存在的
                if instinct_id in self.instincts:
                    # 更新现有本能
                    existing = self.instincts[instinct_id]
                    existing.observation_count += data["count"]
                    self._boost_confidence(instinct_id, Config.BOOST_OBSERVATION, "observation")
                    continue

                # 创建新本能
                confidence = min(0.85, 0.3 + data["count"] * 0.05)

                new_instinct = self.add_instinct(
                    id=instinct_id,
                    trigger=f"when needing to {pattern}",
                    action=f"Use {pattern} tool for this operation",
                    confidence=confidence,
                    domain="workflow",
                    scope="project",
                    evidence=[
                        f"Observed {data['count']} times",
                        f"Across {len(data['sessions'])} sessions"
                    ]
                )

                new_instincts.append(new_instinct)

        return new_instincts

    def cleanup_withered(self) -> Dict[str, int]:
        """清理枯萎的本能到土壤"""
        stats = {"archived": 0, "essence_extracted": 0}

        to_archive = [
            iid for iid, inst in self.instincts.items()
            if inst.lifecycle_stage == "withered"
        ]

        for iid in to_archive:
            instinct = self.instincts[iid]

            # 提取精华
            essence = self._extract_essence(instinct)

            # 移到土壤
            soil_id = f"soil_{iid}"
            self.soil[soil_id] = {
                "id": soil_id,
                "original_id": iid,
                "essence": essence,
                "original_action": instinct.action,
                "original_trigger": instinct.trigger,
                "archived_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "access_count": instinct.access_count,
                "domain": instinct.domain,
                "project_id": instinct.project_id,
            }

            # 从活跃本能中移除
            del self.instincts[iid]

            stats["archived"] += 1
            if essence:
                stats["essence_extracted"] += 1

        self._save_soil()
        self._update_stats()

        return stats

    def _extract_essence(self, instinct: Instinct) -> str:
        """提取精华"""
        lines = []

        # 触发器
        lines.append(f"触发: {instinct.trigger}")

        # 动作（前100字）
        action = instinct.action[:100] + "..." if len(instinct.action) > 100 else instinct.action
        lines.append(f"动作: {action}")

        # 证据
        if instinct.evidence:
            lines.append("证据:")
            for ev in instinct.evidence[:3]:
                lines.append(f"  - {ev}")

        return "\n".join(lines)

    def revive_from_soil(self, soil_id: str) -> Optional[str]:
        """从土壤中复苏本能"""
        if soil_id not in self.soil:
            return None

        soil = self.soil[soil_id]

        # 创建新本能
        new_id = f"revived-{soil['original_id']}"

        new_instinct = self.add_instinct(
            id=new_id,
            trigger=soil["original_trigger"],
            action=soil["original_action"],
            confidence=Config.CONFIDENCE_SPROUT,
            domain=soil.get("domain", "general"),
            scope="project",
            evidence=["Revived from soil archive"]
        )

        # 设置来源
        new_instinct.parent_soil_id = soil_id
        new_instinct.priority = Config.PRIORITY_P1  # 复苏的知识给予较高优先级

        self._save_instinct(new_instinct)

        return new_id

    def decay_all(self) -> Dict[str, int]:
        """执行每日衰减"""
        stats = {"decayed": 0, "withered": 0, "protected": 0}

        for iid, instinct in self.instincts.items():
            # 跳过已归档的
            if instinct.lifecycle_stage == "soil":
                continue

            # 根据优先级决定衰减量
            if instinct.priority == Config.PRIORITY_P0:
                stats["protected"] += 1
                continue

            decay_amount = (Config.DECAY_P2_DAILY if instinct.priority == Config.PRIORITY_P2
                           else Config.DECAY_P1_DAILY)

            new_value = max(0, instinct.confidence - decay_amount)

            if new_value != instinct.confidence:
                old_stage = instinct.lifecycle_stage
                instinct.confidence = new_value
                instinct._update_lifecycle_stage()

                if instinct.lifecycle_stage == "withered" and old_stage != "withered":
                    stats["withered"] += 1
                else:
                    stats["decayed"] += 1

                self._save_instinct(instinct)

        self._update_stats()

        return stats


# ─────────────────────────────────────────────
# CLI 接口
# ─────────────────────────────────────────────

def main():
    """测试统一记忆系统"""
    # 修复 Windows 编码
    if sys.platform == 'win32':
        try:
            import io
            if hasattr(sys.stdout, 'buffer') and sys.stdout.buffer:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        except (ValueError, AttributeError):
            pass

    memory = HomunculusMemory()

    print("=" * 60)
    print("🧠 Homunculus Memory System - 测试")
    print("=" * 60)
    print()

    # 添加测试本能
    print("📝 添加测试本能...")
    memory.add_instinct(
        id="test-git-convention",
        trigger="when committing changes",
        action="Use conventional commits: feat:, fix:, docs:, etc.",
        confidence=0.85,
        domain="workflow",
        scope="project",
        evidence=["User used this pattern 10 times"]
    )

    memory.add_instinct(
        id="test-input-validation",
        trigger="when handling user input",
        action="Always validate and sanitize user input before processing",
        confidence=0.95,
        domain="security",
        scope="global",
        priority=Config.PRIORITY_P0,
        evidence=["Security best practice"]
    )

    print("✅ 已添加 2 个本能\n")

    # 显示状态
    print(memory.get_status_report())
    print()

    # 测试搜索
    print("🔍 测试搜索 'git'...")
    results = memory.search("git")
    for r in results:
        print(f"  {r['instinct'].get_status_icon()} {r['instinct'].id} "
              f"(置信度: {r['confidence']:.2f})")
    print()

    # 模拟衰减
    print("⏰ 模拟一天后的衰减...")
    decay_stats = memory.decay_all()
    print(f"  衰减: {decay_stats['decayed']} 个")
    print(f"  枯萎: {decay_stats['withered']} 个")
    print(f"  保护: {decay_stats['protected']} 个")
    print()

    print(memory.get_status_report())


if __name__ == "__main__":
    main()
