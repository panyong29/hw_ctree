# WiFi XML 配置编辑器
# AI項目
基于 Python 标准库 Tkinter 的跨平台桌面工具，用于修改设备 XML 配置中的 WiFi 参数。

程序不会自动加载任何文件。启动后请点击“打开”，选择需要修改的 XML 配置文件。

## 功能

- 读取 `LANDevice/LANDeviceInstance/WLANConfiguration`
- 显示 `NumberOfInstances` 声明数量和实际读取数量
- 选择具体的 `WLANConfigurationInstance`
- 修改 SSID、WiFi 密码、无线标准、信道和带宽
- 同步修改 `Standard` 与 `X_HW_Standard`
- 修改 `X_HW_HT20` 和 `X_HW_OperatingChannelBandwidth`
- 按 SSID、实例属性或属性值搜索配置
- 保存前自动生成 `.bak` 备份
- 保存后重新解析 XML，确认文件格式有效

## 使用 EXE

Windows 用户可以直接运行：

```text
dist/WiFiXmlEditor.exe
```

运行 EXE 不需要安装 Python。启动后点击“打开”选择 XML 文件。

当前发布的 EXE 使用 Python 3.10 和 Tkinter 打包，适用于 Windows 10/11。Windows 7 的兼容性取决于系统补丁、运行库和显卡环境，建议在目标系统实测。

## 从源码运行

需要 Python 3.6 或更高版本，并且 Python 必须包含 Tkinter。

```bash
python xml_config_editor.py
```

Windows：

```powershell
py -3 xml_config_editor.py
```

如果出现 `ModuleNotFoundError: No module named 'tkinter'`，请安装包含 Tcl/Tk 的完整 Python 发行版。

快捷键：

- `Ctrl+O`：打开 XML
- `Ctrl+S`：保存 XML

## WiFi 参数说明

无线标准：

| XML 标准 | WiFi 代际 |
| --- | --- |
| `11bgn` | WiFi 4 |
| `11ac` | WiFi 5 |
| `11ax` | WiFi 6 |
| `11be` | WiFi 7 |

`Standard` 和 `X_HW_Standard` 必须保持一致，程序的常用设置区会同时修改这两个字段。

常见带宽配置：

| 标准 | `X_HW_HT20` | `X_HW_OperatingChannelBandwidth` | 含义 |
| --- | --- | --- | --- |
| `11bgn` | `1` | `20MHz` | 锁定 20 MHz |
| `11bgn` | `0` | `20MHz` | 自动 20/40 MHz |
| `11be` | `3` | `40MHz` | 自动 20/40/80 MHz |
| `11be` | `4` | `160MHz` | 40 MHz / 160 MHz |

其他字段：

- `SSID`：无线网络名称
- `Channel=0`：自动选择信道
- `PreSharedKey/PreSharedKeyInstance/PreSharedKey`：WiFi 密码

保存时会使用 UTF-8 和缩进格式，XML 的空格和换行可能变化，但节点与属性内容会保留。

## 从源码打包

使用 Python 3.10 和 PyInstaller：

```powershell
py -3.10 -m pip install PyInstaller==5.13.2
py -3.10 -m PyInstaller --noconfirm --clean --onefile --windowed --name WiFiXmlEditor xml_config_editor.py
```

生成文件位于：

```text
dist/WiFiXmlEditor.exe
```

## 安全提示

设备 XML 可能包含以下敏感信息：

- WiFi 密码
- 管理员密码哈希
- 设备令牌和密钥
- 云平台地址、账号或认证信息
- 设备 MAC 地址和局域网设备信息

不要把真实设备配置文件直接提交到公开 GitHub 仓库。建议只上传脱敏后的示例 XML，并在 `.gitignore` 中排除真实配置和备份文件。
