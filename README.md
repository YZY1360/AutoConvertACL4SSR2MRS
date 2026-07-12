# AutoConvertACL4SSR2MRS

Auto-convert [ACL4SSR](https://github.com/ACL4SSR/ACL4SSR) Clash rules to [mihomo](https://github.com/MetaCubeX/mihomo) binary MRS format for faster rule matching.

## How it works

- MRS only supports `domain` and `ipcidr` behaviors — they cannot be mixed in a single file
- Each ACL4SSR `.list` file is automatically split into:
  - `<name>_domain.mrs` — domain rules (DOMAIN, DOMAIN-SUFFIX, DOMAIN-KEYWORD, DOMAIN-REGEX)
  - `<name>_ipcidr.mrs` — IP CIDR rules (IP-CIDR, IP-CIDR6, SRC-IP-CIDR)
- Updated daily via GitHub Actions

## Usage

Use `rule-providers` in your mihomo config:

```yaml
rule-providers:
  # Domain rules
  Telegram:
    type: http
    behavior: domain
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/Telegram_domain.mrs"
    path: ./ruleset/Telegram_domain.mrs
    interval: 86400

  # IP CIDR rules
  Telegram_ipcidr:
    type: http
    behavior: ipcidr
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/Telegram_ipcidr.mrs"
    path: ./ruleset/Telegram_ipcidr.mrs
    interval: 86400

  # Pure IP rules (e.g. China IP ranges)
  ChinaIp:
    type: http
    behavior: ipcidr
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/ChinaIp_ipcidr.mrs"
    path: ./ruleset/ChinaIp_ipcidr.mrs
    interval: 86400

  # GFWList proxy rules
  ProxyGFWlist:
    type: http
    behavior: domain
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/ProxyGFWlist_domain.mrs"
    path: ./ruleset/ProxyGFWlist_domain.mrs
    interval: 86400

  # Ad blocking
  BanAD:
    type: http
    behavior: domain
    format: mrs
    url: "https://raw.githubusercontent.com/YZY1360/AutoConvertACL4SSR2MRS/main/mrs/BanAD_domain.mrs"
    path: ./ruleset/BanAD_domain.mrs
    interval: 86400
```

## Local conversion

```bash
# 1. Download mihomo
curl -L -o mihomo.gz "https://github.com/MetaCubeX/mihomo/releases/download/v1.19.28/mihomo-linux-amd64-v1.19.28.gz"
gunzip mihomo.gz && chmod +x mihomo

# 2. Clone ACL4SSR
git clone https://github.com/ACL4SSR/ACL4SSR.git --depth 1

# 3. Convert
python3 convert.py ACL4SSR/Clash mrs/ ./mihomo
```
