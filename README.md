# AutoConvertACL4SSR2MRS

将 [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR) 的 Clash 规则自动转换为 [mihomo](https://github.com/MetaCubeX/mihomo) 二进制 MRS 格式，提升规则匹配效率。

## 工作原理

- MRS 只支持 `domain` 和 `ipcidr` 两种行为类型，不能混合
- 每个 ACL4SSR `.list` 文件会被自动分离：
  - `<name>.mrs` → 域名规则（DOMAIN, DOMAIN-SUFFIX, DOMAIN-KEYWORD, DOMAIN-REGEX）
  - `<name>_ip.mrs` → IP CIDR 规则（IP-CIDR, IP-CIDR6, SRC-IP-CIDR）
- 通过 GitHub Actions 每天自动更新

## 使用方法

在 mihomo 配置中使用 `rule-providers`：

```yaml
rule-providers:
  # 域名类规则
  Telegram:
    type: http
    behavior: domain
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/Telegram.mrs"
    path: ./ruleset/Telegram.mrs
    interval: 86400

  # IP 类规则（同名 _ip 后缀）
  Telegram_ip:
    type: http
    behavior: ipcidr
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/Telegram_ip.mrs"
    path: ./ruleset/Telegram_ip.mrs
    interval: 86400

  # 纯 IP 规则（如中国 IP 段）
  ChinaIp:
    type: http
    behavior: ipcidr
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/ChinaIp_ip.mrs"
    path: ./ruleset/ChinaIp_ip.mrs
    interval: 86400

  # GFWList 代理规则
  ProxyGFWlist:
    type: http
    behavior: domain
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/ProxyGFWlist.mrs"
    path: ./ruleset/ProxyGFWlist.mrs
    interval: 86400

  # 去广告规则
  BanAD:
    type: http
    behavior: domain
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/BanAD.mrs"
    path: ./ruleset/BanAD.mrs
    interval: 86400
```

## 本地使用

```bash
# 1. 下载 mihomo
curl -L -o mihomo.gz "https://github.com/MetaCubeX/mihomo/releases/download/v1.19.28/mihomo-linux-amd64-v1.19.28.gz"
gunzip mihomo.gz && chmod +x mihomo

# 2. 克隆 ACL4SSR
git clone https://github.com/ACL4SSR/ACL4SSR.git --depth 1

# 3. 转换
python3 convert.py ACL4SSR/Clash mrs/ ./mihomo
```
