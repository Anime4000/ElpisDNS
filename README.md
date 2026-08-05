![SakurakoWaifu](img/banner0.jpg)

# ΕΛΠΙΣ DNS

Community-driven DNS infrastructure focused on privacy, low latency routing, CDN acceleration, and resilient accessibility across regional and international networks. Built upon the principles of an open internet and aligned with the vision of [EFF Internet Freedom and Privacy](https://www.eff.org/). 

## DNS infrastructure focused on

- Privacy
- CDN acceleration
- DNS64/NAT64
- Internet freedom
- Regional routing optimization

# Contributing
Before submitting a pull request, please verify your changes locally.

Start a local HTTP server:
```
python -m http.server 8000
```
Review your changes in the browser before opening a pull request.

# Usage

Quick way to use our DNS Resolver

## Mikrotik
### Configure basic DNS
First, configure your router DNS settings:
```rsc
/ip dns
set servers=1.0.0.1,1.1.1.1 allow-remote-requests=yes
```

### Add DNS over HTTPS Forwarders
Configure ΕΛΠΙΣ DNS DoH endpoints:
```rsc
/ip dns forwarders
add doh-servers="https://b.hitoha.moe/dns-query,https://c.hitoha.moe/dns-query,https://gg.hitoha.moe/dns-query" name=AdGuard
```

### Add Static DNS Entries
Add bootstrap IP addresses for DoH endpoints:
```rsc
/ip dns static
add address=151.158.198.53 name=b.hitoha.moe type=A
add address=160.187.96.67 name=c.hitoha.moe type=A
add address=103.131.188.71 name=gg.hitoha.moe type=A
add name=* forward-to=AdGuard type=FWD
```

# Sponsor
Proudly Sponsored by [Perfect Network](https://perfect.my/) ([AS154516](https://bgp.tools/as/154516))

![PERFECT](img/perfect.png)
