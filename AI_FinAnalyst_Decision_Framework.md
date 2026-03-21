# AI金融分析师 - 决策框架与快速参考

> 将知识转化为可执行的投资决策

---

## 🎯 核心决策框架

### 第一层：市场环境判断

```python
class MarketRegimeDetector:
    """市场环境识别器"""

    def detect_regime(self, market_data: pd.DataFrame) -> str:
        """
        识别当前市场环境

        Returns:
            'bull_trend': 牛市趋势
            'bear_trend': 熊市趋势
            'sideways': 震荡市
            'high_volatility': 高波动
        """
        # 趋势判断
        ma_short = market_data['close'].rolling(20).mean()
        ma_long = market_data['close'].rolling(60).mean()

        # 波动率判断
        volatility = market_data['close'].pct_change().rolling(20).std()
        vol_threshold = volatility.quantile(0.7)

        # 决策逻辑
        if ma_short.iloc[-1] > ma_long.iloc[-1]:
            if volatility.iloc[-1] > vol_threshold:
                return 'bull_trend_high_vol'
            else:
                return 'bull_trend'
        elif ma_short.iloc[-1] < ma_long.iloc[-1]:
            if volatility.iloc[-1] > vol_threshold:
                return 'bear_trend_high_vol'
            else:
                return 'bear_trend'
        else:
            return 'sideways'

# 根据市场环境选择策略
STRATEGY_MAP = {
    'bull_trend': ['momentum', 'growth', 'breakout'],
    'bear_trend': ['short', 'defensive', 'quality'],
    'sideways': ['mean_reversion', 'pairs_trading', 'income'],
    'high_volatility': ['volatility_trading', 'option_strategies']
}
```

### 第二层：股票筛选

```python
class StockScreener:
    """股票筛选器"""

    def screen(self,
               universe: List[str],
               criteria: Dict) -> List[str]:
        """
        根据多维度标准筛选股票

        Criteria:
            - market_cap: 最小市值
            - volume: 最小成交量
            - trend: 趋势要求 ('up', 'down', 'any')
            - valuation: 估值要求 (PE, PB范围)
            - quality: 质量要求 (ROE, 负债率等)
        """
        screened = []

        for symbol in universe:
            # 获取数据
            data = self.get_stock_data(symbol)

            # 应用筛选条件
            if self._check_criteria(data, criteria):
                screened.append(symbol)

        return screened

    def _check_criteria(self, data: pd.DataFrame, criteria: Dict) -> bool:
        """检查单只股票是否符合条件"""
        # 市值筛选
        if 'market_cap' in criteria:
            if data['market_cap'] < criteria['market_cap']:
                return False

        # 流动性筛选
        if 'volume' in criteria:
            if data['volume'].mean() < criteria['volume']:
                return False

        # 趋势筛选
        if 'trend' in criteria:
            ma_short = data['close'].rolling(20).mean().iloc[-1]
            ma_long = data['close'].rolling(60).mean().iloc[-1]

            if criteria['trend'] == 'up' and ma_short < ma_long:
                return False
            elif criteria['trend'] == 'down' and ma_short > ma_long:
                return False

        # 估值筛选
        if 'valuation' in criteria:
            pe = data.get('pe_ratio', 0)
            if pe < criteria['valuation']['pe_min'] or \
               pe > criteria['valuation']['pe_max']:
                return False

        # 质量筛选
        if 'quality' in criteria:
            roe = data.get('roe', 0)
            if roe < criteria['quality']['min_roe']:
                return False

        return True
```

### 第三层：买入决策

```python
class BuyDecisionEngine:
    """买入决策引擎"""

    def make_decision(self,
                     stock: str,
                     analysis: Dict) -> Tuple[bool, float, str]:
        """
        做出买入决策

        Returns:
            (should_buy, confidence, reason)
        """
        score = 0
        reasons = []

        # 1. 技术面评分 (0-40分)
        tech_score, tech_reasons = self._technical_analysis(analysis['technical'])
        score += tech_score
        reasons.extend(tech_reasons)

        # 2. 基本面评分 (0-30分)
        fund_score, fund_reasons = self._fundamental_analysis(analysis['fundamental'])
        score += fund_score
        reasons.extend(fund_reasons)

        # 3. 情绪面评分 (0-20分)
        sent_score, sent_reasons = self._sentiment_analysis(analysis['sentiment'])
        score += sent_score
        reasons.extend(sent_reasons)

        # 4. 风险评分 (0-10分)
        risk_score, risk_reasons = self._risk_analysis(analysis['risk'])
        score += risk_score
        reasons.extend(risk_reasons)

        # 决策阈值
        confidence = score / 100

        should_buy = score >= 60  # 60分以上才买入

        reason_str = "; ".join(reasons)

        return should_buy, confidence, reason_str

    def _technical_analysis(self, technical: Dict) -> Tuple[int, List[str]]:
        """技术面分析"""
        score = 0
        reasons = []

        # 趋势分析
        if technical['trend'] == 'up':
            score += 15
            reasons.append("上升趋势")

        # 动量分析
        if technical['rsi'] < 70:
            score += 10
            reasons.append("RSI未超买")

        # MACD
        if technical['macd_cross'] == 'golden':
            score += 10
            reasons.append("MACD金叉")

        # 成交量
        if technical['volume_increasing']:
            score += 5
            reasons.append("放量上涨")

        return score, reasons

    def _fundamental_analysis(self, fundamental: Dict) -> Tuple[int, List[str]]:
        """基本面分析"""
        score = 0
        reasons = []

        # 估值
        if fundamental['pe'] < 25:
            score += 10
            reasons.append("估值合理")

        # 盈利能力
        if fundamental['roe'] > 0.15:
            score += 10
            reasons.append("ROE优秀")

        # 成长性
        if fundamental['revenue_growth'] > 0.15:
            score += 10
            reasons.append("高成长")

        return score, reasons
```

### 第四层：仓位管理

```python
class PositionManager:
    """仓位管理器"""

    def calculate_position_size(self,
                               account_value: float,
                               stock_data: Dict,
                               strategy_params: Dict) -> int:
        """
        计算仓位大小

        Args:
            account_value: 账户总值
            stock_data: 股票数据
            strategy_params: 策略参数

        Returns:
            股数
        """
        # 方法1: 固定比例
        if strategy_params['method'] == 'fixed_percent':
            position_value = account_value * strategy_params['percent']
            shares = int(position_value / stock_data['price'])

        # 方法2: 凯利公式
        elif strategy_params['method'] == 'kelly':
            win_rate = strategy_params['win_rate']
            avg_win = strategy_params['avg_win']
            avg_loss = strategy_params['avg_loss']

            kelly_f = self._kelly_criterion(win_rate, avg_win, avg_loss)
            position_value = account_value * kelly_f
            shares = int(position_value / stock_data['price'])

        # 方法3: 风险平价
        elif strategy_params['method'] == 'risk_parity':
            risk_amount = account_value * strategy_params['risk_percent']
            stop_distance = stock_data['price'] * strategy_params['stop_percent']
            shares = int(risk_amount / stop_distance)

        # 最大仓位限制
        max_position = account_value * 0.2  # 单个股票最大20%
        max_shares = int(max_position / stock_data['price'])

        return min(shares, max_shares)

    def _kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """凯利公式"""
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - p

        kelly_f = (b * p - q) / b
        half_kelly = max(0, kelly_f / 2)  # 使用半凯利更保守

        return half_kelly
```

### 第五层：止损与止盈

```python
class ExitManager:
    """退出管理器"""

    def should_exit(self,
                   position: Dict,
                   current_data: Dict) -> Tuple[bool, str]:
        """
        判断是否应该退出

        Returns:
            (should_exit, reason)
        """
        entry_price = position['entry_price']
        current_price = current_data['price']
        stop_loss = position['stop_loss']
        take_profit = position['take_profit']
        highest_price = position.get('highest_price', entry_price)

        # 更新最高价
        highest_price = max(highest_price, current_price)

        # 1. 止损检查
        if current_price <= stop_loss:
            return True, f"触发止损 {stop_loss:.2f}"

        # 2. 止盈检查
        if current_price >= take_profit:
            return True, f"触发止盈 {take_profit:.2f}"

        # 3. 移动止损
        if position.get('trailing_stop', False):
            trailing_stop = highest_price * 0.9  # 回撤10%止损
            if current_price <= trailing_stop:
                return True, f"触发移动止损 {trailing_stop:.2f}"

        # 4. 时间止损
        days_held = (current_data['date'] - position['entry_date']).days
        if days_held > position.get('max_days', 90):
            return True, f"持有时间超过{position['max_days']}天"

        # 5. 信号反转
        if current_data.get('signal_reversed', False):
            return True, "交易信号反转"

        # 6. 基本面恶化
        if current_data.get('fundamental_deteriorated', False):
            return True, "基本面恶化"

        return False, ""
```

---

## 📊 完整决策流程

```python
class TradingSystem:
    """完整交易系统"""

    def __init__(self, config: Dict):
        self.config = config
        self.regime_detector = MarketRegimeDetector()
        self.screener = StockScreener()
        self.buy_engine = BuyDecisionEngine()
        self.position_manager = PositionManager()
        self.exit_manager = ExitManager()

    def run_daily_routine(self, date: str):
        """每日交易例程"""

        print(f"\n{'='*60}")
        print(f"日期: {date}")
        print(f"{'='*60}")

        # Step 1: 市场环境识别
        market_data = self.get_market_data()
        regime = self.regime_detector.detect_regime(market_data)
        print(f"\n✓ 市场环境: {regime}")

        # Step 2: 选择策略
        active_strategies = STRATEGY_MAP.get(regime, ['default'])
        print(f"✓ 激活策略: {active_strategies}")

        # Step 3: 股票筛选
        universe = self.get_stock_universe()
        screened = self.screener.screen(universe, self.config['screening_criteria'])
        print(f"✓ 筛选结果: {len(screened)} 只股票")

        # Step 4: 逐个分析
        for stock in screened:
            print(f"\n分析 {stock}...")

            # 获取分析数据
            analysis = self.get_comprehensive_analysis(stock)

            # 买入决策
            should_buy, confidence, reason = self.buy_engine.make_decision(stock, analysis)

            if should_buy:
                print(f"  ✓ 建议买入 (置信度: {confidence:.2%})")
                print(f"  理由: {reason}")

                # 计算仓位
                account_value = self.get_account_value()
                stock_data = self.get_stock_data(stock)
                shares = self.position_manager.calculate_position_size(
                    account_value, stock_data, self.config['position_params']
                )

                # 计算止损止盈
                entry_price = stock_data['price']
                stop_loss = entry_price * 0.95  # 5%止损
                take_profit = entry_price * 1.15  # 15%止盈

                print(f"  建议仓位: {shares} 股")
                print(f"  止损: {stop_loss:.2f}")
                print(f"  止盈: {take_profit:.2f}")

                # 检查风险
                if self.check_risk_limits(stock, shares, entry_price):
                    # 执行买入
                    self.execute_buy(stock, shares, entry_price)
                    print(f"  ✓ 已执行买入")
                else:
                    print(f"  ✗ 超过风险限制，未执行")
            else:
                print(f"  ✗ 不建议买入 (置信度: {confidence:.2%})")
                print(f"  理由: {reason}")

        # Step 5: 检查现有持仓
        print(f"\n✓ 检查持仓 ({len(self.positions)} 个)")
        for position in self.positions:
            current_data = self.get_stock_data(position['symbol'])

            should_exit, reason = self.exit_manager.should_exit(position, current_data)

            if should_exit:
                print(f"  {position['symbol']}: {reason}")
                self.execute_sell(position['symbol'], position['shares'])
                print(f"  ✓ 已卖出")
            else:
                pnl = self.calculate_pnl(position, current_data['price'])
                print(f"  {position['symbol']}: 持有中 (盈亏: {pnl:.2%})")

        # Step 6: 风险检查
        self.check_portfolio_risk()

        # Step 7: 生成报告
        self.generate_daily_report(date)

        print(f"\n{'='*60}\n")
```

---

## 🎓 实战检查清单

### 开盘前检查

```
□ 宏观环境
  □ 美联储利率决议
  □ 重要经济数据发布
  □ 地缘政治事件
  □ 大公司财报

□ 市场环境
  □ 主要指数趋势（S&P 500, 纳指, 上证指数）
  □ VIX恐慌指数
  □ 市场宽度（涨跌家数比）
  □ 北向资金流向

□ 持仓检查
  □ 预期公告（财报、分红）
  □ 技术关键位置
  □ 止损止盈设置
```

### 盘中监控

```
□ 价格异动
  □ 突破关键阻力/支撑
  □ 放量突破/破位
  □ 尾盘拉升/砸盘

□ 持仓管理
  □ 止损触发检查
  □ 止盈触发检查
  □ 加仓/减仓机会

□ 新闻监控
  □ 公司公告
  □ 行业新闻
  □ 政策变化
```

### 收盘后复盘

```
□ 市场总结
  □ 指数涨跌
  □ 成交量变化
  □ 热点板块

□ 持仓复盘
  □ 盈亏情况
  □ 交易是否按计划执行
  □ 错误和教训

□ 明日计划
  □ 关注股票列表
  □ 关键价格位
  □ 预期事件
```

---

## 🔧 快速参考代码片段

### 1. 获取数据

```python
import yfinance as yf

# 快速获取数据
def get_data(symbol, period='1y'):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    return df

# 批量获取
symbols = ['AAPL', 'MSFT', 'GOOGL']
data = {s: get_data(s) for s in symbols}
```

### 2. 计算指标

```python
# 简单移动平均
df['MA20'] = df['Close'].rolling(20).mean()
df['MA60'] = df['Close'].rolling(60).mean()

# RSI
delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
df['RSI'] = 100 - (100 / (1 + rs))

# 布林带
df['BB_middle'] = df['Close'].rolling(20).mean()
df['BB_std'] = df['Close'].rolling(20).std()
df['BB_upper'] = df['BB_middle'] + 2 * df['BB_std']
df['BB_lower'] = df['BB_middle'] - 2 * df['BB_std']
```

### 3. 生成信号

```python
# 金叉死叉
df['signal'] = 0
df.loc[df['MA20'] > df['MA60'], 'signal'] = 1  # 金叉
df.loc[df['MA20'] < df['MA60'], 'signal'] = -1  # 死叉

# 只在交叉点交易
df['positions'] = df['signal'].diff()
```

### 4. 回测

```python
# 简单回测
initial_capital = 100000
capital = initial_capital
shares = 0

for i in range(1, len(df)):
    if df['positions'].iloc[i] == 1:  # 买入信号
        price = df['Close'].iloc[i]
        shares = (capital * 0.95) // price
        capital -= shares * price
    elif df['positions'].iloc[i] == -1:  # 卖出信号
        price = df['Close'].iloc[i]
        capital += shares * price
        shares = 0

# 最终价值
final_value = capital + shares * df['Close'].iloc[-1]
total_return = (final_value / initial_capital - 1) * 100
print(f"总收益率: {total_return:.2f}%")
```

### 5. 可视化

```python
import matplotlib.pyplot as plt

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

# K线图和均线
ax1.plot(df.index, df['Close'], label='Close')
ax1.plot(df.index, df['MA20'], label='MA20')
ax1.plot(df.index, df['MA60'], label='MA60')
ax1.set_title('Price and Moving Averages')
ax1.legend()

# RSI
ax2.plot(df.index, df['RSI'])
ax2.axhline(70, color='r', linestyle='--')
ax2.axhline(30, color='g', linestyle='--')
ax2.set_title('RSI')

# MACD
ax3.plot(df.index, df['MACD'], label='MACD')
ax3.plot(df.index, df['Signal'], label='Signal')
ax3.bar(df.index, df['Histogram'], label='Histogram')
ax3.set_title('MACD')
ax3.legend()

plt.tight_layout()
plt.show()
```

---

## ⚠️ 常见错误与解决方案

### 错误1: 过拟合

**症状**: 回测收益率很高，实盘却亏损

**原因**:
- 策略参数过度优化
- 使用了未来数据
- 样本量太小

**解决**:
```python
# 使用样本外测试
train_data = data[:'2023']
test_data = data['2023':]

# 简化策略
# 避免：if rsi > 30 and rsi < 35 and macd > 0.01 and ...
# 推荐：if rsi < 30 and macd > 0

# 交叉验证
from sklearn.model_selection import cross_val_score
scores = cross_val_score(model, X, y, cv=5)
```

### 错误2: 忽略交易成本

**症状**: 回测盈利，实盘亏损

**原因**: 没有考虑手续费、滑点

**解决**:
```python
# 添加手续费
commission = 0.001  # 0.1%
cost = shares * price * (1 + commission)

# 添加滑点
slippage = 0.0005  # 0.05%
execution_price = price * (1 + slippage)
```

### 错误3: 风险集中

**症状**: 单只股票亏损导致大幅回撤

**原因**: 单个仓位过大

**解决**:
```python
# 限制单个仓位
max_position_percent = 0.2  # 最大20%
position_value = account_value * max_position_percent

# 分散投资
num_positions = 10
position_value = account_value / num_positions
```

### 错误4: 情绪化交易

**症状**: 不按策略执行，追涨杀跌

**原因**: 没有严格的交易纪律

**解决**:
```python
# 自动化交易
def auto_trade():
    signal = strategy.generate_signal()
    if signal == 'buy' and not has_position():
        execute_buy()
    elif signal == 'sell' and has_position():
        execute_sell()

# 设置硬止损
def check_stop_loss():
    for position in positions:
        if position.price < position.stop_loss:
            execute_sell(position.symbol)
```

---

## 📈 进阶技巧

### 1. 多周期分析

```python
# 分析多个时间周期
def multi_timeframe_analysis(symbol):
    timeframes = {
        'daily': '1y',
        'weekly': '5y',
        'monthly': '10y'
    }

    signals = {}
    for tf, period in timeframes.items():
        data = get_data(symbol, period)
        signals[tf] = analyze_trend(data)

    # 只有当多周期信号一致时才交易
    if all(s == 'bullish' for s in signals.values()):
        return 'strong_buy'
    elif all(s == 'bearish' for s in signals.values()):
        return 'strong_sell'
    else:
        return 'wait'
```

### 2. 相关性分析

```python
# 计算股票相关性
def calculate_correlation(symbols, period='1y'):
    returns = pd.DataFrame()
    for symbol in symbols:
        data = get_data(symbol, period)
        returns[symbol] = data['Close'].pct_change()

    corr_matrix = returns.corr()
    return corr_matrix

# 避免同时持有高相关性的股票
def check_portfolio_correlation(portfolio, threshold=0.7):
    corr = calculate_correlation(portfolio)
    high_corr_pairs = []

    for i in range(len(corr.columns)):
        for j in range(i+1, len(corr.columns)):
            if corr.iloc[i, j] > threshold:
                high_corr_pairs.append((
                    corr.columns[i],
                    corr.columns[j],
                    corr.iloc[i, j]
                ))

    return high_corr_pairs
```

### 3. 事件驱动策略

```python
# 财报前后的价格模式
def earnings_pattern(symbol, lookback=8):
    ticker = yf.Ticker(symbol)
    earnings = ticker.earnings

    patterns = []
    for date in earnings.index:
        # 财报前后的价格变化
        before = get_data(symbol, start=date-lookback, end=date)
        after = get_data(symbol, start=date, end=date+lookback)

        patterns.append({
            'date': date,
            'before_return': before['Close'].pct_change().sum(),
            'after_return': after['Close'].pct_change().sum()
        })

    return patterns
```

### 4. 动态仓位调整

```python
# 根据市场波动率调整仓位
def dynamic_position_sizing(market_volatility, base_position=0.1):
    """
    市场波动大时减仓，波动小时加仓
    """
    vol_normalized = (market_volatility - market_volatility.mean()) / market_volatility.std()

    if vol_normalized > 2:  # 高波动
        return base_position * 0.5
    elif vol_normalized < -2:  # 低波动
        return base_position * 1.5
    else:
        return base_position
```

---

## 🎯 实战建议

### 心态管理

1. **接受不确定性**
   - 没有人能100%预测市场
   - 专注于概率，而不是确定性
   - 小概率事件一定会发生

2. **长期视角**
   - 不要被短期波动影响
   - 关注策略的长期期望值
   - 避免频繁交易

3. **持续学习**
   - 市场在不断进化
   - 保持好奇心
   - 从错误中学习

### 系统优化

1. **从简单开始**
   - 先实现简单策略
   - 验证有效性后再优化
   - 避免过度复杂

2. **记录一切**
   - 交易日志
   - 决策理由
   - 结果分析

3. **定期回顾**
   - 每周回顾
   - 每月总结
   - 每年评估

### 风险管理黄金法则

```
1. 永远不要在没有止损的情况下交易
2. 单个交易风险不超过账户的2%
3. 总仓位不超过账户的80%
4. 保持现金储备
5. 分散投资
6. 不在情绪波动时交易
7. 不追逐热门股票
8. 承认错误，及时止损
9. 让利润奔跑，及时止损
10. 专注于过程，而不是结果
```

---

这个决策框架为你提供了从分析到执行的完整路径。记住：**在金融市场中，没有圣杯，只有概率和纪律。**
