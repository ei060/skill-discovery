# AI金融分析师 - 实战项目框架

> 将知识体系转化为可执行的投资决策系统

---

## 📁 项目结构

```
AI_Financial_Analyst/
│
├── data/                          # 数据层
│   ├── collectors/                # 数据采集器
│   │   ├── price_collector.py
│   │   ├── fundamental_collector.py
│   │   ├── news_collector.py
│   │   └── alternative_collector.py
│   ├── processors/                # 数据处理器
│   │   ├── cleaner.py
│   │   ├── feature_engineering.py
│   │   └── normalizer.py
│   └── storage/                   # 数据存储
│       ├── database.py
│       └── cache.py
│
├── analysis/                      # 分析层
│   ├── technical/                 # 技术分析
│   │   ├── indicators.py
│   │   ├── patterns.py
│   │   └── ta_helpers.py
│   ├── fundamental/               # 基本面分析
│   │   ├── ratios.py
│   │   ├── valuation.py
│   │   └── scoring.py
│   ├── sentiment/                 # 情绪分析
│   │   ├── nlp_processor.py
│   │   ├── social_analyzer.py
│   │   └── news_sentiment.py
│   └── ml_models/                 # 机器学习模型
│       ├── predictors/
│       │   ├── price_predictor.py
│       │   ├── trend_classifier.py
│       │   └── volatility_model.py
│       ├── deep_learning/
│       │   ├── lstm_model.py
│       │   ├── transformer_model.py
│       │   └── multimodal_fusion.py
│       └── reinforcement_learning/
│           ├── trading_agent.py
│           └── environment.py
│
├── strategies/                    # 策略层
│   ├── base_strategy.py           # 基础策略类
│   ├── technical_strategies/      # 技术分析策略
│   │   ├── ma_crossover.py
│   │   ├── mean_reversion.py
│   │   └── breakout.py
│   ├── fundamental_strategies/    # 基本面策略
│   │   ├── value_investing.py
│   │   ├── growth_investing.py
│   │   └── quality_scoring.py
│   ├── quant_strategies/          # 量化策略
│   │   ├── multi_factor.py
│   │   ├── pairs_trading.py
│   │   └── statistical_arb.py
│   └── ai_strategies/             # AI增强策略
│       ├── ml_strategy.py
│       ├── dl_strategy.py
│       └── ensemble_strategy.py
│
├── backtest/                      # 回测系统
│   ├── engine.py                  # 回测引擎
│   ├── metrics.py                 # 绩效指标
│   ├── analyzer.py                # 分析器
│   └── visualizer.py              # 可视化
│
├── risk/                          # 风险管理
│   ├── position_sizing.py         # 仓位管理
│   ├── stop_loss.py               # 止损策略
│   ├── portfolio_opt.py           # 组合优化
│   └── stress_test.py             # 压力测试
│
├── execution/                     # 执行层
│   ├── brokers/                   # 券商接口
│   │   ├── base_broker.py
│   │   ├── paper_trading.py       # 模拟交易
│   │   └── live_trading.py        # 实盘交易
│   ├── order_manager.py           # 订单管理
│   └── execution_algorithm.py     # 执行算法
│
├── monitoring/                    # 监控系统
│   ├── logger.py                  # 日志
│   ├── alerts.py                  # 告警
│   ├── dashboard.py               # 仪表板
│   └── reports.py                 # 报告生成
│
├── utils/                         # 工具函数
│   ├── config.py                  # 配置管理
│   ├── helpers.py                 # 辅助函数
│   └── decorators.py              # 装饰器
│
├── notebooks/                     # Jupyter笔记本
│   ├── research/                  # 研究笔记
│   ├── experiments/               # 实验记录
│   └── tutorials/                 # 教程
│
├── tests/                         # 测试
│   ├── unit/                      # 单元测试
│   ├── integration/               # 集成测试
│   └── data/                      # 测试数据
│
├── configs/                       # 配置文件
│   ├── default.yaml
│   ├── production.yaml
│   └── strategies/                # 策略配置
│
├── main.py                        # 主入口
├── requirements.txt               # 依赖
├── setup.py                       # 安装脚本
└── README.md                      # 项目说明
```

---

## 🏗️ 核心模块实现

### 1. 数据采集模块

```python
# data/collectors/price_collector.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import asyncio
import aiohttp

class PriceCollector:
    """价格数据采集器"""

    def __init__(self):
        self.cache = {}

    def collect_historical(self,
                          symbols: List[str],
                          start_date: str,
                          end_date: str,
                          interval: str = '1d') -> Dict[str, pd.DataFrame]:
        """
        批量采集历史数据

        Args:
            symbols: 股票代码列表
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            interval: 数据间隔 (1d, 1wk, 1h, 5m, etc.)

        Returns:
            {symbol: DataFrame} 字典
        """
        data = {}

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(
                    start=start_date,
                    end=end_date,
                    interval=interval
                )

                # 标准化列名
                df.columns = [col.lower() for col in df.columns]
                data[symbol] = df

                print(f"✓ Collected {symbol}: {len(df)} records")

            except Exception as e:
                print(f"✗ Error collecting {symbol}: {e}")

        return data

    def collect_realtime(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        采集实时数据

        Args:
            symbols: 股票代码列表

        Returns:
            {symbol: {price, change, volume, ...}}
        """
        realtime_data = {}

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info

                realtime_data[symbol] = {
                    'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                    'change': info.get('regularMarketChangePercent'),
                    'volume': info.get('regularMarketVolume'),
                    'high_52w': info.get('fiftyTwoWeekHigh'),
                    'low_52w': info.get('fiftyTwoWeekLow'),
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('forwardPE'),
                    'timestamp': datetime.now()
                }

            except Exception as e:
                print(f"✗ Error getting realtime data for {symbol}: {e}")

        return realtime_data

    def save_to_database(self, data: Dict[str, pd.DataFrame], db_path: str):
        """
        保存到数据库
        """
        import sqlite3

        conn = sqlite3.connect(db_path)

        for symbol, df in data.items():
            # 清理表名
            table_name = symbol.replace('.', '_').replace('-', '_')
            df.to_sql(table_name, conn, if_exists='replace', index=True)

        conn.close()
        print(f"✓ Saved {len(data)} symbols to database")

# data/collectors/fundamental_collector.py
class FundamentalCollector:
    """基本面数据采集器"""

    def __init__(self):
        pass

    def collect_financials(self, symbol: str) -> Dict:
        """
        采集财务数据
        """
        ticker = yf.Ticker(symbol)

        # 获取财务报表
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        cash_flow = ticker.cashflow

        # 获取关键指标
        info = ticker.info

        return {
            'income_statement': financials,
            'balance_sheet': balance_sheet,
            'cash_flow': cash_flow,
            'key_metrics': {
                'pe_ratio': info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'ps_ratio': info.get('priceToSalesTrailing12Months'),
                'ev_ebitda': info.get('enterpriseToEbitda'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'roe': info.get('returnOnEquity'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth')
            }
        }

    def collect_earnings(self, symbol: str) -> pd.DataFrame:
        """
        采集业绩数据
        """
        ticker = yf.Ticker(symbol)
        earnings = ticker.earnings
        return earnings

# data/collectors/news_collector.py
import requests
from datetime import datetime

class NewsCollector:
    """新闻数据采集器"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # 可以使用 NewsAPI, Bing News, 等服务

    def collect_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """
        采集新闻
        """
        # 示例：使用Yahoo Finance新闻
        ticker = yf.Ticker(symbol)
        news = ticker.news

        processed_news = []
        for item in news:
            processed_news.append({
                'title': item['title'],
                'link': item['link'],
                'published': datetime.fromtimestamp(item['providerPublishTime']),
                'source': item['publisher'],
                'summary': item.get('summary', '')
            })

        return processed_news

    def analyze_sentiment(self, news_list: List[Dict]) -> Dict:
        """
        分析新闻情绪
        """
        from transformers import pipeline

        # 使用预训练的情绪分析模型
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=" ProsusAI/finbert"  # 金融领域的BERT模型
        )

        sentiments = []
        for news in news_list:
            result = sentiment_pipeline(news['title'] + ' ' + news['summary'])
            sentiments.append({
                'timestamp': news['published'],
                'sentiment': result[0]['label'],
                'score': result[0]['score']
            })

        # 计算平均情绪
        avg_sentiment = sum(
            1 if s['sentiment'] == 'POSITIVE' else
            -1 if s['sentiment'] == 'NEGATIVE' else 0
            for s in sentiments
        ) / len(sentiments)

        return {
            'sentiments': sentiments,
            'average_sentiment': avg_sentiment,
            'sentiment_trend': self._calculate_trend(sentiments)
        }

    def _calculate_trend(self, sentiments: List[Dict]) -> str:
        """计算情绪趋势"""
        if len(sentiments) < 2:
            return 'neutral'

        recent = sentiments[-3:]
        recent_avg = sum(
            1 if s['sentiment'] == 'POSITIVE' else
            -1 if s['sentiment'] == 'NEGATIVE' else 0
            for s in recent
        ) / len(recent)

        if recent_avg > 0.3:
            return 'improving'
        elif recent_avg < -0.3:
            return 'deteriorating'
        else:
            return 'stable'
```

### 2. 技术分析模块

```python
# analysis/technical/indicators.py
import pandas as pd
import numpy as np
from typing import Tuple

class TechnicalIndicators:
    """技术指标计算器"""

    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """简单移动平均"""
        return data.rolling(window=period).mean()

    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """指数移动平均"""
        return data.ewm(span=period, adjust=False).mean()

    @staticmethod
    def macd(data: pd.Series,
             fast: int = 12,
             slow: int = 26,
             signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD指标

        Returns:
            (macd_line, signal_line, histogram)
        """
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)

        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = (macd_line - signal_line) * 2

        return macd_line, signal_line, histogram

    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """RSI指标"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def bollinger_bands(data: pd.Series,
                       period: int = 20,
                       std_dev: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        布林带

        Returns:
            (upper_band, middle_band, lower_band)
        """
        middle_band = TechnicalIndicators.sma(data, period)
        std = data.rolling(period).std()

        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band, middle_band, lower_band

    @staticmethod
    def stochastic(high: pd.Series,
                  low: pd.Series,
                  close: pd.Series,
                  period: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        KDJ指标

        Returns:
            (k, d, j)
        """
        low_min = low.rolling(period).min()
        high_max = high.rolling(period).max()

        rsv = (close - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(span=3, adjust=False).mean()
        d = k.ewm(span=3, adjust=False).mean()
        j = 3 * k - 2 * d

        return k, d, j

    @staticmethod
    def atr(high: pd.Series,
            low: pd.Series,
            close: pd.Series,
            period: int = 14) -> pd.Series:
        """ATR（平均真实波幅）"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(period).mean()

        return atr

    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """OBV（能量潮）"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    def add_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加所有技术指标到DataFrame
        """
        df = df.copy()

        # 移动平均
        df['sma_5'] = self.sma(df['close'], 5)
        df['sma_10'] = self.sma(df['close'], 10)
        df['sma_20'] = self.sma(df['close'], 20)
        df['sma_60'] = self.sma(df['close'], 60)
        df['ema_12'] = self.ema(df['close'], 12)
        df['ema_26'] = self.ema(df['close'], 26)

        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = self.macd(df['close'])

        # RSI
        df['rsi'] = self.rsi(df['close'])

        # 布林带
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = self.bollinger_bands(df['close'])
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])

        # KDJ
        df['kdj_k'], df['kdj_d'], df['kdj_j'] = self.stochastic(
            df['high'], df['low'], df['close']
        )

        # ATR
        df['atr'] = self.atr(df['high'], df['low'], df['close'])

        # OBV
        df['obv'] = self.obv(df['close'], df['volume'])

        # 收益率
        df['returns'] = df['close'].pct_change()
        df['log_returns'] = np.log(df['close'] / df['close'].shift(1))

        # 波动率
        df['volatility_20'] = df['returns'].rolling(20).std()
        df['volatility_60'] = df['returns'].rolling(60).std()

        return df

# analysis/technical/patterns.py
class PatternRecognizer:
    """K线形态识别"""

    @staticmethod
    def is_doji(df: pd.DataFrame, i: int, tolerance: float = 0.1) -> bool:
        """
        识别十字星
        """
        row = df.iloc[i]
        body = abs(row['close'] - row['open'])
        range_price = row['high'] - row['low']

        if range_price == 0:
            return False

        return body / range_price < tolerance

    @staticmethod
    def is_hammer(df: pd.DataFrame, i: int) -> bool:
        """
        识别锤子线
        """
        row = df.iloc[i]
        body = abs(row['close'] - row['open'])
        upper_shadow = row['high'] - max(row['open'], row['close'])
        lower_shadow = min(row['open'], row['close']) - row['low']

        # 下影线长度是实体的2倍以上
        # 上影线很短
        return (lower_shadow >= 2 * body and
                upper_shadow < body * 0.3 and
                body > 0)

    @staticmethod
    def detect_engulfing(df: pd.DataFrame, i: int) -> str:
        """
        识别吞噬形态
        Returns: 'bullish' or 'bearish' or None
        """
        if i < 1:
            return None

        prev = df.iloc[i-1]
        curr = df.iloc[i]

        prev_body = abs(prev['close'] - prev['open'])
        curr_body = abs(curr['close'] - curr['open'])

        # 看涨吞噬
        if (prev['close'] < prev['open'] and  # 前一根是阴线
            curr['close'] > curr['open'] and  # 当前是阳线
            curr['open'] < prev['close'] and  # 当前开盘低于前收盘
            curr['close'] > prev['open']):    # 当前收盘高于前开盘
            return 'bullish'

        # 看跌吞噬
        if (prev['close'] > prev['open'] and  # 前一根是阳线
            curr['close'] < curr['open'] and  # 当前是阴线
            curr['open'] > prev['close'] and  # 当前开盘高于前收盘
            curr['close'] < prev['open']):    # 当前收盘低于前开盘
            return 'bearish'

        return None

    def detect_all_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        识别所有形态
        """
        patterns = pd.DataFrame(index=df.index)
        patterns['doji'] = False
        patterns['hammer'] = False
        patterns['bullish_engulfing'] = False
        patterns['bearish_engulfing'] = False

        for i in range(1, len(df)):
            if self.is_doji(df, i):
                patterns.loc[df.index[i], 'doji'] = True

            if self.is_hammer(df, i):
                patterns.loc[df.index[i], 'hammer'] = True

            engulfing = self.detect_engulfing(df, i)
            if engulfing == 'bullish':
                patterns.loc[df.index[i], 'bullish_engulfing'] = True
            elif engulfing == 'bearish':
                patterns.loc[df.index[i], 'bearish_engulfing'] = True

        return patterns
```

### 3. 机器学习预测模块

```python
# analysis/ml_models/price_predictor.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib

class PricePredictor:
    """价格预测器"""

    def __init__(self, model_type='rf'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None

    def prepare_features(self, df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
        """
        准备特征

        Args:
            df: 包含价格和技术指标的DataFrame
            lookback: 回看天数
        """
        features = pd.DataFrame(index=df.index)

        # 技术指标
        if 'rsi' in df.columns:
            features['rsi'] = df['rsi']

        if 'macd' in df.columns:
            features['macd'] = df['macd']
            features['macd_signal'] = df['macd_signal']
            features['macd_hist'] = df['macd_hist']

        if 'bb_position' in df.columns:
            features['bb_position'] = df['bb_position']
            features['bb_width'] = df['bb_width']

        # 价格动量
        for period in [1, 3, 5, 10]:
            features[f'momentum_{period}'] = df['close'].pct_change(period)

        # 波动率
        features['volatility'] = df['returns'].rolling(20).std()

        # 成交量变化
        if 'volume' in df.columns:
            features['volume_change'] = df['volume'].pct_change()
            features['volume_ma_ratio'] = df['volume'] / df['volume'].rolling(20).mean()

        # 价格位置
        features['price_to_ma20'] = df['close'] / df['sma_20']
        features['price_to_ma60'] = df['close'] / df['sma_60']

        # 趋势强度
        features['trend_strength'] = (df['sma_5'] > df['sma_20']).astype(int)

        # 历史收益率（滞后）
        for lag in range(1, lookback + 1):
            features[f'return_lag_{lag}'] = df['returns'].shift(lag)

        return features

    def create_target(self, df: pd.DataFrame,
                     forward_days: int = 5,
                     threshold: float = 0.02) -> pd.Series:
        """
        创建目标变量

        Args:
            forward_days: 向前看的天数
            threshold: 涨跌幅阈值

        Returns:
            1=涨, 0=横盘, -1=跌
        """
        future_returns = df['close'].shift(-forward_days) / df['close'] - 1

        target = pd.Series(0, index=df.index)
        target[future_returns > threshold] = 1
        target[future_returns < -threshold] = -1

        return target

    def train(self, df: pd.DataFrame, test_size: float = 0.2):
        """
        训练模型
        """
        # 准备特征和目标
        features = self.prepare_features(df)
        target = self.create_target(df)

        # 删除缺失值
        valid_idx = features.notna().all(axis=1) & target.notna()
        features = features[valid_idx]
        target = target[valid_idx]

        self.feature_names = features.columns.tolist()

        # 划分训练测试集
        X_train, X_test, y_train, y_test = train_test_split(
            features, target, test_size=test_size, shuffle=False
        )

        # 标准化
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # 训练模型
        if self.model_type == 'rf':
            self.model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'gb':
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )

        self.model.fit(X_train_scaled, y_train)

        # 评估
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)

        # 交叉验证
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, cv=5, n_jobs=-1
        )

        print(f"Train Accuracy: {train_score:.3f}")
        print(f"Test Accuracy: {test_score:.3f}")
        print(f"CV Accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")

        # 特征重要性
        if hasattr(self.model, 'feature_importances_'):
            importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)

            print("\nTop 10 Important Features:")
            print(importance.head(10))

        return {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'cv_accuracy': cv_scores.mean(),
            'feature_importance': importance
        }

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        预测
        """
        features = self.prepare_features(df)
        features_scaled = self.scaler.transform(features)

        # 预测概率
        proba = self.model.predict_proba(features_scaled)

        return proba

    def save_model(self, filepath: str):
        """保存模型"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }, filepath)

    def load_model(self, filepath: str):
        """加载模型"""
        data = joblib.load(filepath)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.model_type = data['model_type']
```

### 4. 回测系统

```python
# backtest/engine.py
import pandas as pd
import numpy as np
from typing import Dict, List, Callable

class BacktestEngine:
    """回测引擎"""

    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.trades = []
        self.portfolio_value = []

    def run(self,
            data: pd.DataFrame,
            strategy: Callable,
            commission: float = 0.001,
            slippage: float = 0.0001) -> pd.DataFrame:
        """
        运行回测

        Args:
            data: 价格数据
            strategy: 策略函数，返回交易信号
            commission: 手续费率
            slippage: 滑点

        Returns:
            包含净值、持仓等信息的DataFrame
        """
        results = pd.DataFrame(index=data.index)
        results['signal'] = strategy(data)
        results['price'] = data['close']
        results['position'] = 0
        results['holdings'] = 0
        results['cash'] = self.initial_capital
        results['total'] = self.initial_capital
        results['returns'] = 0

        cash = self.initial_capital
        position = 0

        for i in range(1, len(data)):
            signal = results['signal'].iloc[i]
            price = data['close'].iloc[i]

            # 买入
            if signal == 1 and position == 0:
                # 考虑滑点
                execution_price = price * (1 + slippage)
                shares = (cash * 0.95) // execution_price  # 保留5%现金
                if shares > 0:
                    cost = shares * execution_price * (1 + commission)
                    cash -= cost
                    position = shares

                    self.trades.append({
                        'date': data.index[i],
                        'action': 'buy',
                        'price': execution_price,
                        'shares': shares,
                        'cost': cost
                    })

            # 卖出
            elif signal == -1 and position > 0:
                execution_price = price * (1 - slippage)
                proceeds = position * execution_price * (1 - commission)
                cash += proceeds

                self.trades.append({
                    'date': data.index[i],
                    'action': 'sell',
                    'price': execution_price,
                    'shares': position,
                    'proceeds': proceeds
                })

                position = 0

            # 更新组合价值
            holdings_value = position * price
            total = cash + holdings_value

            results.loc[data.index[i], 'position'] = position
            results.loc[data.index[i], 'holdings'] = holdings_value
            results.loc[data.index[i], 'cash'] = cash
            results.loc[data.index[i], 'total'] = total

            # 计算收益率
            if i > 0:
                results.loc[data.index[i], 'returns'] = total / results['total'].iloc[i-1] - 1

        return results

# backtest/metrics.py
class PerformanceMetrics:
    """绩效指标计算"""

    @staticmethod
    def calculate_all(results: pd.DataFrame,
                     benchmark_returns: pd.Series = None) -> Dict:
        """
        计算所有绩效指标
        """
        returns = results['returns'].fillna(0)

        metrics = {}

        # 收益指标
        metrics['total_return'] = (results['total'].iloc[-1] / results['total'].iloc[0] - 1) * 100

        trading_days = len(results)
        metrics['annual_return'] = (
            (results['total'].iloc[-1] / results['total'].iloc[0]) **
            (252 / trading_days) - 1
        ) * 100

        # 风险指标
        metrics['volatility'] = returns.std() * np.sqrt(252) * 100

        # 夏普比率（假设无风险利率3%）
        risk_free_rate = 0.03
        excess_returns = returns - risk_free_rate / 252
        metrics['sharpe_ratio'] = returns.mean() / returns.std() * np.sqrt(252)

        # 最大回撤
        cummax = results['total'].cummax()
        drawdown = (results['total'] - cummax) / cummax
        metrics['max_drawdown'] = drawdown.min() * 100

        # 胜率
        winning_trades = len([t for t in returns if t > 0])
        total_trades = len([t for t in returns if t != 0])
        metrics['win_rate'] = winning_trades / total_trades * 100 if total_trades > 0 else 0

        # 盈亏比
        wins = [t for t in returns if t > 0]
        losses = [t for t in returns if t < 0]
        if wins and losses:
            metrics['profit_loss_ratio'] = np.mean(wins) / abs(np.mean(losses))
        else:
            metrics['profit_loss_ratio'] = 0

        # Calmar比率（年化收益/最大回撤）
        metrics['calmar_ratio'] = abs(metrics['annual_return'] / metrics['max_drawdown'])

        # Sortino比率（只考虑下行波动）
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0:
            downside_std = downside_returns.std() * np.sqrt(252)
            metrics['sortino_ratio'] = (metrics['annual_return'] - risk_free_rate * 100) / downside_std
        else:
            metrics['sortino_ratio'] = 0

        # 相对指标（如果有基准）
        if benchmark_returns is not None:
            benchmark_aligned = benchmark_returns.reindex(returns.index).fillna(0)
            metrics['alpha'] = (returns.mean() - benchmark_aligned.mean()) * 252 * 100
            metrics['beta'] = np.cov(returns, benchmark_aligned)[0, 1] / benchmark_aligned.var()

        return metrics

    @staticmethod
    def print_report(metrics: Dict):
        """打印绩效报告"""
        print("=" * 60)
        print("回测绩效报告")
        print("=" * 60)
        print(f"总收益率:        {metrics['total_return']:.2f}%")
        print(f"年化收益率:      {metrics['annual_return']:.2f}%")
        print(f"年化波动率:      {metrics['volatility']:.2f}%")
        print(f"夏普比率:        {metrics['sharpe_ratio']:.2f}")
        print(f"最大回撤:        {metrics['max_drawdown']:.2f}%")
        print(f"胜率:            {metrics['win_rate']:.2f}%")
        print(f"盈亏比:          {metrics['profit_loss_ratio']:.2f}")
        print(f"Calmar比率:      {metrics['calmar_ratio']:.2f}")
        print(f"Sortino比率:     {metrics['sortino_ratio']:.2f}")

        if 'alpha' in metrics:
            print(f"Alpha:           {metrics['alpha']:.2f}%")
            print(f"Beta:            {metrics['beta']:.2f}")

        print("=" * 60)
```

### 5. 完整示例：使用整个系统

```python
# example_complete_system.py
import pandas as pd
from data.collectors.price_collector import PriceCollector
from analysis.technical.indicators import TechnicalIndicators
from analysis.ml_models.price_predictor import PricePredictor
from backtest.engine import BacktestEngine
from backtest.metrics import PerformanceMetrics

def main():
    # 1. 数据采集
    print("Step 1: Collecting data...")
    collector = PriceCollector()
    data = collector.collect_historical(
        symbols=['AAPL', 'MSFT', 'GOOGL'],
        start_date='2020-01-01',
        end_date='2024-12-31'
    )

    # 使用AAPL作为示例
    df = data['AAPL']
    print(f"Collected {len(df)} days of data")

    # 2. 计算技术指标
    print("\nStep 2: Calculating technical indicators...")
    ta = TechnicalIndicators()
    df_with_indicators = ta.add_all_indicators(df)
    print(f"Added {len(df_with_indicators.columns) - len(df.columns)} indicators")

    # 3. 训练ML模型
    print("\nStep 3: Training ML model...")
    predictor = PricePredictor(model_type='rf')
    metrics = predictor.train(df_with_indicators)

    # 4. 生成交易信号
    print("\nStep 4: Generating trading signals...")

    def ml_strategy(data):
        """
        基于ML的策略
        """
        # 预测
        proba = predictor.predict(data)

        # 只在有足够置信度时交易
        signals = pd.Series(0, index=data.index)
        signals[proba[:, 2] > 0.6] = 1   # 看涨概率>60% -> 买入
        signals[proba[:, 0] > 0.6] = -1  # 看跌概率>60% -> 卖出

        return signals

    # 5. 回测
    print("\nStep 5: Running backtest...")
    engine = BacktestEngine(initial_capital=100000)
    results = engine.run(df_with_indicators, ml_strategy)

    # 6. 计算绩效
    print("\nStep 6: Calculating performance metrics...")
    perf_metrics = PerformanceMetrics.calculate_all(results)
    PerformanceMetrics.print_report(perf_metrics)

    # 7. 保存结果
    print("\nStep 7: Saving results...")
    results.to_csv('backtest_results.csv')
    predictor.save_model('price_predictor.pkl')

    print("\n✓ Complete!")

if __name__ == '__main__':
    main()
```

---

## 📋 requirements.txt

```txt
# 数据获取
yfinance>=0.2.28
pandas-datareader>=0.10.0

# 数据处理
pandas>=2.0.0
numpy>=1.24.0

# 技术分析
ta>=0.11.0
TA-Lib>=0.4.28

# 机器学习
scikit-learn>=1.3.0
xgboost>=2.0.0
lightgbm>=4.0.0

# 深度学习
torch>=2.1.0
tensorflow>=2.15.0

# NLP
transformers>=4.35.0
sentencepiece>=0.1.99

# 回测
backtrader>=1.9.78
zipline-reloaded>=3.0.0

# 优化
scipy>=1.11.0
cvxpy>=1.4.0

# 可视化
matplotlib>=3.8.0
plotly>=5.18.0
seaborn>=0.13.0

# 数据库
sqlalchemy>=2.0.0
sqlite3

# 工具
requests>=2.31.0
python-dotenv>=1.0.0
pyyaml>=6.0.0
joblib>=1.3.0

# Jupyter
jupyter>=1.0.0
ipywidgets>=8.1.0

# OpenBB
openbb>=4.0.0

# 监控
telegram-send>=0.37
```

---

## 🚀 快速开始

```bash
# 1. 克隆项目
git clone https://github.com/yourusername/AI_Financial_Analyst.git
cd AI_Financial_Analyst

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行示例
python example_complete_system.py

# 5. 启动Jupyter
jupyter notebook

# 6. 查看notebook教程
# notebooks/tutorials/01_data_collection.ipynb
# notebooks/tutorials/02_technical_analysis.ipynb
# notebooks/tutorials/03_machine_learning.ipynb
# notebooks/tutorials/04_backtesting.ipynb
```

---

## 📊 项目扩展方向

1. **多资产组合**
   - 股票、债券、商品、加密货币
   - 跨资产相关性分析
   - 动态资产配置

2. **高频交易**
   - Tick级数据处理
   - 低延迟执行
   - 做市策略

3. **另类数据**
   - 卫星图像
   - 信用卡数据
   - 社交媒体情绪
   - 网络流量

4. **深度强化学习**
   - 端到端学习
   - 自适应策略
   - 多智能体系统

5. **可解释性AI**
   - 特征归因
   - 决策可视化
   - 模型诊断

---

这个实战框架为你提供了从零构建AI交易系统的完整路线图。记住：**先理解，再实现；先回测，后实盘；风控第一，持续优化！**
