# KEEY AI 报价系统 - Cloudflare Tunnel 部署说明

## 一、下载安装 cloudflared

1. 打开下载地址：

   https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

2. 下载 `cloudflared-windows-amd64.exe`

3. 将文件改名为：

   ```
   cloudflared.exe
   ```

4. 放到：

   ```
   C:\Windows\System32
   ```

## 二、启动步骤

### 第一步

双击：

```
deploy/start_server.bat
```

启动 Flask 报价系统。

### 第二步

双击：

```
deploy/start_tunnel.bat
```

控制台会输出：

```
https://xxxxx.trycloudflare.com
```

手机浏览器输入该网址即可访问，无需连接电脑 WiFi。

## 三、一键启动（推荐）

直接双击：

```
一键启动.bat
```

会自动：

1. 启动 Flask
2. 启动 Cloudflare Tunnel
3. 输出公网访问地址

## 四、注意事项

- 电脑必须保持开机。
- Flask 必须运行。
- Cloudflare Tunnel 关闭后网址失效。
- 每次启动都会生成新的临时网址。

## 五、不要修改的内容

不要修改报价逻辑、Excel、数据库、AI 解析。
本目录只包含部署辅助文件。
