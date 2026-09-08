# WiFi XML 配置编辑器

当前版本：`1.0.1`

基于 Python 标准库 Tkinter 的跨平台桌面工具，用于修改设备 XML 配置中的 WiFi 参数。

程序不会自动加载任何文件。启动后请点击“打开”，选择需要修改的 XML 配置文件。

## 新手声明

本工具适合只需要修改 WiFi 基本参数的用户。打开配置后，建议只使用界面上方的“常用 WiFi 设置”区域，修改 SSID、密码、无线标准、信道。

“全部属性”区域是给熟悉设备 XML 数据模型的用户使用的。不了解字段用途时，请不要自行修改；如需了解某个字段，请先在 AI 工具中搜索和确认其含义，再决定是否修改。

不同厂商、型号和固件版本的网页菜单名称可能不同，本文只描述通用流程，不保证每台设备的菜单名称完全一致。

## 设备配置操作流程

### 1. 从设备网页导出配置

1. 用浏览器登录设备管理网页。
2. 在“系统管理”“维护”“配置管理”“备份与恢复”或类似页面中，找到配置导出、配置备份或导出 XML 的功能。
3. 导出配置文件到电脑，并保留一份原始文件作为备份。
4. 不要直接在原始文件上覆盖保存，建议先复制一份工作副本。

### 2. 使用工具修改 WiFi

1. 打开 `WiFiXmlEditor.exe`，或使用 Python 运行程序。
2. 点击“打开”，选择刚才导出的工作副本。
3. 在左侧选择需要修改的 WLAN 配置。
4. 只在“常用 WiFi 设置”区域修改参数。
5. 点击“应用常用 WiFi 设置”，确认左侧 SSID、标准和启用状态显示正确。
6. 点击“保存”或“另存为”。程序会在保存前生成 `.bak` 备份，并在保存后校验 XML。

### 3. 导回设备网页

1. 回到设备网页的“配置管理”“备份与恢复”或类似页面。
2. 找到配置导入、配置恢复或上传配置文件功能。
3. 先确认设备当前配置已经备份，再选择修改后的 XML 文件上传。
4. 按设备网页提示执行应用配置、重启或恢复操作。
5. 设备重启期间不要断电、不要关闭网页或拔出网线。
6. 重启完成后，检查 SSID、密码和 WiFi 频段是否符合预期。

如果导入失败或设备无法正常工作，请使用设备网页的恢复功能导入原始备份；如果设备没有恢复入口，请按照设备厂商的恢复方式操作。

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
dist/WiFiXmlEditor-1.0.1.exe
```

运行 EXE 不需要安装 Python。启动后点击“打开”选择 XML 文件。

当前发布的 EXE 使用 Python 3.10 和 Tkinter 打包，适用于 Windows 10/11。Windows 7 的兼容性取决于系统补丁、运行库和显卡环境，建议在目标系统实测。

EXE 约 10 MB 属于正常情况，不是打包错误。单文件程序需要同时包含 Python 运行时、Tkinter/Tcl/Tk 图形库、XML 标准库和程序本身，因此无法压缩到 1 MB 以内。即使使用 UPX，通常也只能减少一部分体积，不能接近 1 MB。

如果必须控制在 1 MB 以内，只能不打包 Python，改为要求用户安装 Python 和 Tkinter 后运行 `.py` 文件，或者使用 C/C++ 等原生语言重写程序。

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

| XML 标准  | WiFi 代际 |
| --------- | --------- |
| `11bgn` | WiFi 4    |
| `11ac`  | WiFi 5    |
| `11ax`  | WiFi 6    |
| `11be`  | WiFi 7    |

`Standard` 和 `X_HW_Standard` 必须保持一致，程序的常用设置区会同时修改这两个字段。

常见带宽配置：

| 标准      | `X_HW_HT20` | `X_HW_OperatingChannelBandwidth` | 含义                                               |
| --------- | ------------- | ---------------------------------- | -------------------------------------------------- |
| `11bgn` | `1`         | `20MHz`                          | 锁定 20 MHz                                        |
| `11bgn` | `0`         | `20MHz`                          | 自动 20/40 MHz                                     |
| `11be`  | `4`         | `40MHz`                          | 锁定 160 MHz                                       |
| `11be`  | `3`         | `40MHz`                          | 固件相关：可能锁定 80 MHz，也可能自动 20/40/80 MHz |

示例：

```xml
<!-- WiFi 4，锁定 20 MHz -->
<WLANConfigurationInstance Standard="11bgn" X_HW_Standard="11bgn"
	X_HW_HT20="1" X_HW_OperatingChannelBandwidth="20MHz" />

<!-- WiFi 4，自动 20/40 MHz -->
<WLANConfigurationInstance Standard="11bgn" X_HW_Standard="11bgn"
	X_HW_HT20="0" X_HW_OperatingChannelBandwidth="20MHz" />

<!-- WiFi 7，锁定 160 MHz -->
<WLANConfigurationInstance Standard="11be" X_HW_Standard="11be"
	X_HW_HT20="4" X_HW_OperatingChannelBandwidth="40MHz" />

<!-- WiFi 7；部分固件表现为自动 20/40/80 MHz，部分固件可能锁定 80 MHz -->
<WLANConfigurationInstance Standard="11be" X_HW_Standard="11be"
	X_HW_HT20="3" X_HW_OperatingChannelBandwidth="40MHz" />
```

WiFi 7 下 `X_HW_HT20` 还可能出现空值、`0`、`1` 或 `2`。这些取值的实际效果依赖设备固件，建议逐项修改并在设备上验证；程序不会替用户推断这些未确认的映射。

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
