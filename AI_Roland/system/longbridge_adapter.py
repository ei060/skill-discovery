#!/usr/bin/env python3
"""
长桥证券行情适配器

功能:
- 实时行情订阅 (港股/美股/A股通)
- K线数据获取
- 实时报价推送
- 与现有 ai_buffett_pro.py 系统集成

配置文件: AI_Roland/记忆库/知识库/longbridge_config.json
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
import threading

logger = logging.getLogger(__name__)

# 尝试导入长桥 SDK
try:
    from longbridge.openapi import QuoteContext
    # 尝试导入其他组件（可能不存在）
    try:
        from longbridge.openapi import SubType, Period, Market
    except ImportError:
        # 创建简化版本
        class SubType:
            Quote = "quote"
        class Period:
            Min_1 = "1m"
            Min_5 = "5m"
            Min_15 = "15m"
            Min_30 = "30m"
            Hour = "1H"
            Day = "1D"
            Week = "1W"
            Month = "1M"
        class Market:
            HK = "HK"
            US = "US"
            CN = "CN"
    LONGBRIDGE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"长桥 SDK 未安装: {e}")
    LONGBRIDGE_AVAILABLE = False
    QuoteContext = None


class LongBridgeConfig:
    """长桥配置管理"""

    DEFAULT_CONFIG_PATH = Path("D:/ClaudeWork/AI_Roland/记忆库/知识库/longbridge_config.json")

    @classmethod
    def load(cls) -> Dict[str, Any]:
        """加载配置"""
        if cls.DEFAULT_CONFIG_PATH.exists():
            with open(cls.DEFAULT_CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 默认配置
        return {
            "app_key": "",
            "app_secret": "",
            "access_token": "",
            "http_url": "https://openapi.longbridgehk.com",
            "ws_url": "wss://openapi.longbridgehk.com",
        }

    @classmethod
    def save(cls, config: Dict[str, Any]) -> None:
        """保存配置"""
        cls.DEFAULT_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(cls.DEFAULT_CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logger.info(f"配置已保存: {cls.DEFAULT_CONFIG_PATH}")

    @classmethod
    def validate(cls, config: Dict[str, Any]) -> bool:
        """验证配置"""
        required = ["app_key", "app_secret", "access_token"]
        return all(config.get(k) for k in required)


class LongBridgeQuoteAdapter:
    """
    长桥行情适配器

    支持市场:
    - 港股 (HK): 700.HK, 9988.HK
    - 美股 (US): AAPL, TSLA
    - A股通 (CN/A): 600519.SH (通过沪港通/深港通)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or LongBridgeConfig.load()
        self.quote_ctx: Optional[QuoteContext] = None
        self.connected = False
        self._subscribed_symbols = set()
        self._callbacks = {}  # symbol -> [callbacks]
        self._running = False
        self._thread = None

    def connect(self) -> bool:
        """连接到长桥服务器"""
        if not LONGBRIDGE_AVAILABLE:
            logger.error("长桥 SDK 未安装")
            return False

        if not LongBridgeConfig.validate(self.config):
            logger.error("长桥配置无效，请设置 app_key, app_secret, access_token")
            return False

        try:
            # 创建行情上下文
            self.quote_ctx = QuoteContext(
                app_key=self.config["app_key"],
                app_secret=self.config["app_secret"],
                access_token=self.config["access_token"],
                http_url=self.config.get("http_url"),
                ws_url=self.config.get("ws_url"),
            )

            # 测试连接
            self.connected = True
            logger.info("长桥行情连接成功")
            return True

        except Exception as e:
            logger.error(f"长桥连接失败: {e}")
            return False

    def disconnect(self) -> None:
        """断开连接"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            self._thread = None

        self._subscribed_symbols.clear()
        self._callbacks.clear()

        if self.quote_ctx:
            try:
                self.quote_ctx.close()
            except:
                pass
            self.quote_ctx = None

        self.connected = False
        logger.info("长桥行情已断开")

    def get_realtime_quote(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        获取实时报价

        Args:
            symbols: 代码列表, 如 ["700.HK", "AAPL.US", "600519.SH"]

        Returns:
            {symbol: {price, volume, change, ...}}
        """
        if not self.connected:
            if not self.connect():
                return {}

        result = {}
        try:
            for symbol in symbols:
                try:
                    quote = self.quote_ctx.quote([symbol])[0]
                    result[symbol] = {
                        "symbol": symbol,
                        "name": quote.symbol_name,
                        "price": quote.last_done,
                        "volume": quote.volume,
                        "turnover": quote.turnover,
                        "change": quote.change_rate,
                        "high": quote.high,
                        "low": quote.low,
                        "open": quote.open,
                        "prev_close": quote.prev_close,
                        "timestamp": datetime.now().isoformat(),
                    }
                except Exception as e:
                    logger.warning(f"获取 {symbol} 报价失败: {e}")
                    result[symbol] = {"error": str(e)}

        except Exception as e:
            logger.error(f"批量获取报价失败: {e}")

        return result

    def get_candlesticks(self, symbol: str, period: str = "1D",
                        count: int = 100) -> List[Dict]:
        """
        获取K线数据

        Args:
            symbol: 代码, 如 "700.HK"
            period: 周期 (1m, 5m, 15m, 30m, 1H, 1D, 1W, 1M)
            count: 数量

        Returns:
            K线数据列表
        """
        if not self.connected:
            if not self.connect():
                return []

        # 周期映射
        period_map = {
            "1m": Period.Min_1,
            "5m": Period.Min_5,
            "15m": Period.Min_15,
            "30m": Period.Min_30,
            "1H": Period.Hour,
            "1D": Period.Day,
            "1W": Period.Week,
            "1M": Period.Month,
        }

        lb_period = period_map.get(period, Period.Day)

        try:
            resp = self.quote_ctx.candlesticks(
                symbol=symbol,
                period=lb_period,
                count=count,
            )

            candles = []
            for candle in resp:
                candles.append({
                    "symbol": symbol,
                    "timestamp": candle.timestamp.isoformat(),
                    "open": candle.open,
                    "high": candle.high,
                    "low": candle.low,
                    "close": candle.close,
                    "volume": candle.volume,
                    "turnover": candle.turnover,
                })

            return candles

        except Exception as e:
            logger.error(f"获取K线失败 {symbol}: {e}")
            return []

    def subscribe_quote(self, symbols: List[str],
                       callback: Optional[Callable] = None) -> bool:
        """
        订阅实时行情推送

        Args:
            symbols: 代码列表
            callback: 回调函数 callback(symbol, data)
        """
        if not self.connected:
            if not self.connect():
                return False

        try:
            # 设置回调
            if callback:
                for symbol in symbols:
                    if symbol not in self._callbacks:
                        self._callbacks[symbol] = []
                    self._callbacks[symbol].append(callback)

            # 订阅
            sub_types = [SubType.Quote]
            self.quote_ctx.subscribe(
                symbols=symbols,
                sub_types=sub_types,
            )

            self._subscribed_symbols.update(symbols)
            logger.info(f"订阅行情: {symbols}")
            return True

        except Exception as e:
            logger.error(f"订阅失败: {e}")
            return False

    def unsubscribe_quote(self, symbols: List[str]) -> bool:
        """取消订阅"""
        try:
            if self.quote_ctx:
                self.quote_ctx.unsubscribe(symbols, [SubType.Quote])

            for symbol in symbols:
                self._subscribed_symbols.discard(symbol)
                self._callbacks.pop(symbol, None)

            logger.info(f"取消订阅: {symbols}")
            return True

        except Exception as e:
            logger.error(f"取消订阅失败: {e}")
            return False

    def search_security(self, pattern: str, market: str = "HK") -> List[Dict]:
        """
        搜索证券代码

        Args:
            pattern: 搜索关键词 (代码或名称)
            market: 市场 (HK, US, CN)

        Returns:
            证券列表
        """
        if not self.connected:
            if not self.connect():
                return []

        try:
            # 根据市场搜索
            market_map = {
                "HK": Market.HK,
                "US": Market.US,
                "CN": Market.CN,
            }

            # 简化实现 - 直接使用用户输入的代码
            # 实际可以调用长桥的搜索接口
            return [{
                "symbol": pattern,
                "name": pattern,
                "market": market,
            }]

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return []

    def get_market_status(self) -> Dict[str, bool]:
        """获取各市场交易状态"""
        now = datetime.now()

        # 简化实现 - 实际应从长桥获取
        return {
            "HK": self._is_market_open("HK", now),
            "US": self._is_market_open("US", now),
            "CN": self._is_market_open("CN", now),
        }

    def _is_market_open(self, market: str, now: datetime) -> bool:
        """判断市场是否开盘"""
        weekday = now.weekday()  # 0=周一, 6=周日
        if weekday >= 5:  # 周末
            return False

        hour = now.hour
        minute = now.minute
        time_min = hour * 60 + minute

        if market == "HK":
            # 港股: 9:30-12:00, 13:00-16:00
            return (570 <= time_min < 720) or (780 <= time_min < 960)
        elif market == "US":
            # 美股 EST: 9:30-16:00 (北京时间 21:30-04:00)
            return (1290 <= time_min) or (time_min < 240)
        elif market == "CN":
            # A股: 9:30-11:30, 13:00-15:00
            return (570 <= time_min < 690) or (780 <= time_min < 900)

        return False

    def to_dataframe(self, data: List[Dict]) -> Any:
        """转换为 pandas DataFrame"""
        try:
            import pandas as pd
            return pd.DataFrame(data)
        except ImportError:
            logger.warning("pandas 未安装")
            return data


class LongBridgeQuoteIntegration:
    """与现有系统的集成"""

    def __init__(self):
        self.adapter = LongBridgeQuoteAdapter()

    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        获取股票信息，兼容现有格式

        用于集成到 ai_buffett_pro.py
        """
        quote_data = self.adapter.get_realtime_quote([symbol])

        if symbol not in quote_data:
            return {
                "symbol": symbol,
                "error": "获取失败",
                "timestamp": datetime.now().isoformat(),
            }

        data = quote_data[symbol]
        if "error" in data:
            return data

        # 转换为兼容格式
        return {
            "symbol": symbol,
            "name": data.get("name", symbol),
            "price": data.get("price", 0),
            "change": data.get("change", 0),
            "volume": data.get("volume", 0),
            "high": data.get("high", 0),
            "low": data.get("low", 0),
            "open": data.get("open", 0),
            "timestamp": data.get("timestamp", datetime.now().isoformat()),
            "source": "longbridge",
        }

    def get_history_data(self, symbol: str, days: int = 30) -> Any:
        """获取历史数据，兼容现有格式"""
        candles = self.adapter.get_candlesticks(symbol, period="1D", count=days)

        if not candles:
            return None

        return self.adapter.to_dataframe(candles)


# 测试代码
def test_longbridge():
    """测试长桥连接"""
    print("\n" + "=" * 50)
    print("长桥行情适配器测试")
    print("=" * 50)

    # 加载配置
    config = LongBridgeConfig.load()

    print("\n当前配置:")
    print(f"  App Key: {config.get('app_key', '')[:10]}..." if config.get('app_key') else "  App Key: 未设置")
    print(f"  App Secret: {'已设置' if config.get('app_secret') else '未设置'}")
    print(f"  Access Token: {'已设置' if config.get('access_token') else '未设置'}")

    if not LongBridgeConfig.validate(config):
        print("\n[!] 配置不完整，请先设置长桥 API 密钥")
        print("\n获取方式:")
        print("  1. 访问 https://open.longbridge.com/")
        print("  2. 创建应用获取 App Key 和 App Secret")
        print("  3. 生成 Access Token")
        print(f"  4. 配置保存到: {LongBridgeConfig.DEFAULT_CONFIG_PATH}")
        return

    # 测试连接
    adapter = LongBridgeQuoteAdapter(config)

    if adapter.connect():
        print("\n[OK] 连接成功!")

        # 测试获取行情
        test_symbols = ["700.HK"]  # 腾讯控股
        print(f"\n获取行情: {test_symbols}")
        quotes = adapter.get_realtime_quote(test_symbols)

        for symbol, data in quotes.items():
            if "error" in data:
                print(f"  {symbol}: [X] {data['error']}")
            else:
                print(f"  {symbol}:")
                print(f"    名称: {data.get('name')}")
                print(f"    价格: {data.get('price')}")
                print(f"    成交量: {data.get('volume')}")

        adapter.disconnect()
    else:
        print("\n[X] 连接失败，请检查配置")


if __name__ == "__main__":
    test_longbridge()
