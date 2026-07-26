# GitHub Sponsors 个人开发者可行性报告

> 研究时间：2026-07-26

---

## 一、核心结论

```
❌ 中国大陆个人开发者无法直接使用 GitHub Sponsors
原因：GitHub Sponsors 不支持中国大陆（Mainland China）
       Stripe 不为中国大陆居民提供收款服务
```

**替代方案可行** — 如下。

---

## 二、官方支持的地区

GitHub Sponsors **支持**（部分）：香港、日本、新加坡、台湾、欧盟、美国、英国等

GitHub Sponsors **不支持**：中国大陆、俄罗斯、印度（等）

---

## 三、对中国开发者的三条路

### 方案 A：使用香港 Stripe 账户（推荐 ⭐）

| 步骤 | 说明 |
|------|------|
| 1. 注册 GitHub Sponsors | 在 sponsors 页面申请 |
| 2. 填写 W-8 BEN 税表 | 非美国纳税人必须填 |
| 3. 绑定 Stripe Connect | Stripe 账户需属于 **支持的国家/地区** |
| 4. 通过审核 | GitHub 人工审核（几天） |
| 5. 开始接收赞助 | 每月 22 号 Stripe 打款 |

**关键：** 需要有一个香港（或其他支持地区）的 Stripe 账户。  
如果你有香港银行账户或能注册香港 Stripe，这条路最直接。

### 方案 B：通过 Fiscal Host（财务托管）

```yaml
平台: Open Collective
流程: GitHub Sponsors → Open Collective → 你
费用: Open Collective 收取 10% 平台费
适用: 不想折腾 Stripe 注册
```

### 方案 C：使用第三方捐赠平台（最简单）

| 平台 | 收款方式 | 手续费 | 中国大陆 |
|------|---------|--------|---------|
| **Patreon** | PayPal / Stripe | 5-12% | ✅ 可用 PayPal |
| **Buy Me a Coffee** | Stripe / PayPal | 5% | ✅ 可用 PayPal |
| **Ko-fi** | PayPal / Stripe | 0% (基础版) | ✅ 可用 PayPal |
| **爱发电 (afdian)** | 支付宝/微信 | 6% | ✅ **最方便** |

---

## 四、费用对比

| 平台 | 个人赞助费率 | 企业赞助费率 | 提现费 |
|------|------------|------------|--------|
| **GitHub Sponsors** | **0%** | 6% | Stripe 提现费 |
| Patreon | 5-12% | 同左 | PayPal/Stripe |
| Buy Me a Coffee | 5% | 同左 | PayPal/Stripe |
| Ko-fi | 0% (基础) | 同左 | PayPal 2.9%+$0.30 |
| **爱发电** | **6%** | 同左 | **支付宝/微信** ✅ |

---

## 五、对 StockPulse 的建议

```
当前阶段：项目刚起步，用户量 0 → 暂时不需要 Sponsors
建议路径：

Phase 1（现在）：在 README 放一个 Buy Me a Coffee / 爱发电 链接
              → 零门槛，有爱发电就行（支付宝收款）

Phase 2（有用户后）：申请 GitHub Sponsors（走香港 Stripe）
                 → 在 GitHub 上看到 Sponsors 按钮，增加可信度

Phase 3（有收入后）：考虑 Patreon / 爱发电 会员制
                 → 付费 API Key + 高级功能
```

---

## 六、立即可以做的事

在 README 底部添加赞助链接（零门槛，只需放链接）：

```markdown
## 💖 支持项目

如果 StockPulse 对你有帮助，可以请我喝杯咖啡：

[![爱发电](https://img.shields.io/badge/爱发电-支持-blue)](https://afdian.com/a/your-id)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-支持-yellow)](https://buymeacoffee.com/your-id)
```

建议优先用 **爱发电**（ifdian.net）—— 支付宝/微信收款，中国大陆用户最方便。