import copy
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET


class XmlConfigEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("XML 配置编辑器")
        self.geometry("1180x760")
        self.minsize(900, 560)

        self.xml_path = None
        self.xml_root = None
        self.wlan_container = None
        self.wlan_configurations = []
        self.tree_nodes = {}
        self.attribute_values = {}
        self.selected_element = None
        self.search_matches = []
        self.search_index = -1
        self.dirty = False

        self._build_ui()
        self._bind_shortcuts()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        toolbar = ttk.Frame(self, padding=(8, 8, 8, 4))
        toolbar.grid(row=0, column=0, sticky="ew")
        toolbar.columnconfigure(5, weight=1)

        ttk.Button(toolbar, text="打开", command=self.open_xml).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(toolbar, text="保存", command=self.save_xml).grid(row=0, column=1, padx=5)
        ttk.Button(toolbar, text="另存为", command=self.save_xml_as).grid(row=0, column=2, padx=5)
        ttk.Label(toolbar, text="搜索:").grid(row=0, column=3, padx=(18, 4))
        self.search_value = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_value, width=34)
        search_entry.grid(row=0, column=4, sticky="ew")
        search_entry.bind("<Return>", lambda event: self.search())
        ttk.Button(toolbar, text="查找", command=self.search).grid(row=0, column=5, padx=(5, 0), sticky="w")
        self.status_value = tk.StringVar(value="未加载文件")
        ttk.Label(toolbar, textvariable=self.status_value).grid(row=0, column=6, padx=(15, 0))

        main_pane = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        main_pane.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))

        tree_frame = ttk.Frame(main_pane, padding=4)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.element_tree = ttk.Treeview(tree_frame, show="tree", selectmode="browse")
        self.element_tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.element_tree.yview)
        tree_scroll.grid(row=0, column=1, sticky="ns")
        self.element_tree.configure(yscrollcommand=tree_scroll.set)
        self.element_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        main_pane.add(tree_frame, weight=3)

        editor_frame = ttk.Frame(main_pane, padding=8)
        editor_frame.rowconfigure(4, weight=1)
        editor_frame.columnconfigure(0, weight=1)
        self.element_label = ttk.Label(editor_frame, text="请选择一个 XML 节点", font=("TkDefaultFont", 11, "bold"))
        self.element_label.grid(row=0, column=0, sticky="w", pady=(0, 8))

        quick_frame = ttk.LabelFrame(editor_frame, text="常用 WiFi 设置")
        quick_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        quick_frame.columnconfigure(1, weight=1)
        quick_frame.columnconfigure(3, weight=1)

        ttk.Label(quick_frame, text="SSID 无线名称").grid(row=0, column=0, padx=6, pady=4, sticky="w")
        self.ssid_value = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.ssid_value).grid(row=0, column=1, padx=6, pady=4, sticky="ew")
        ttk.Label(quick_frame, text="密码 PreSharedKey").grid(row=0, column=2, padx=6, pady=4, sticky="w")
        self.password_value = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.password_value, show="*").grid(row=0, column=3, padx=6, pady=4, sticky="ew")

        ttk.Label(quick_frame, text="无线标准").grid(row=1, column=0, padx=6, pady=4, sticky="w")
        self.standard_value = tk.StringVar()
        ttk.Combobox(
            quick_frame,
            textvariable=self.standard_value,
            values=("11bgn", "11ac", "11ax", "11be"),
            state="readonly",
        ).grid(row=1, column=1, padx=6, pady=4, sticky="ew")
        ttk.Label(quick_frame, text="X_HW_HT20").grid(row=1, column=2, padx=6, pady=4, sticky="w")
        self.ht20_value = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.ht20_value, width=10).grid(row=1, column=3, padx=6, pady=4, sticky="w")

        ttk.Label(quick_frame, text="工作带宽").grid(row=2, column=0, padx=6, pady=4, sticky="w")
        self.bandwidth_value = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.bandwidth_value).grid(row=2, column=1, padx=6, pady=4, sticky="ew")
        ttk.Label(quick_frame, text="信道 Channel").grid(row=2, column=2, padx=6, pady=4, sticky="w")
        self.channel_value = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.channel_value).grid(row=2, column=3, padx=6, pady=4, sticky="ew")

        help_text = (
            "标准: 11bgn=WiFi4，11ac=WiFi5，11ax=WiFi6，11be=WiFi7；"
            "Standard 与 X_HW_Standard 会同时修改。\n"
            "11bgn + HT20=1 + 20MHz=锁定20MHz；HT20=0 + 20MHz=自动20/40MHz；"
            "11be + HT20=3=自动20/40/80MHz，HT20=4=40MHz/160MHz。\n"
            "Channel=0 表示自动选择信道；密码写入 PreSharedKeyInstance 的 PreSharedKey。"
        )
        ttk.Label(quick_frame, text=help_text, justify="left", wraplength=760).grid(
            row=3, column=0, columnspan=4, padx=6, pady=(4, 6), sticky="w"
        )
        ttk.Button(quick_frame, text="应用常用 WiFi 设置", command=self.apply_wifi_settings).grid(
            row=4, column=0, columnspan=4, padx=6, pady=(0, 6), sticky="w"
        )

        ttk.Label(editor_frame, text="全部属性（双击属性值编辑）").grid(row=2, column=0, sticky="w")

        attributes_frame = ttk.Frame(editor_frame)
        attributes_frame.grid(row=3, column=0, sticky="nsew", pady=(4, 8))
        attributes_frame.rowconfigure(0, weight=1)
        attributes_frame.columnconfigure(0, weight=1)
        self.attribute_table = ttk.Treeview(
            attributes_frame,
            columns=("name", "value"),
            show="headings",
            selectmode="browse",
        )
        self.attribute_table.heading("name", text="属性")
        self.attribute_table.heading("value", text="值")
        self.attribute_table.column("name", width=220, stretch=False)
        self.attribute_table.column("value", width=420, stretch=True)
        self.attribute_table.grid(row=0, column=0, sticky="nsew")
        attribute_scroll = ttk.Scrollbar(attributes_frame, orient=tk.VERTICAL, command=self.attribute_table.yview)
        attribute_scroll.grid(row=0, column=1, sticky="ns")
        self.attribute_table.configure(yscrollcommand=attribute_scroll.set)
        self.attribute_table.bind("<Double-1>", self.begin_attribute_edit)

        self.attribute_edit = ttk.Entry(editor_frame)
        self.attribute_edit.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        self.attribute_edit.bind("<Return>", lambda event: self.apply_attribute())
        ttk.Button(editor_frame, text="应用属性修改", command=self.apply_attribute).grid(row=5, column=0, sticky="w")
        main_pane.add(editor_frame, weight=5)

    def _bind_shortcuts(self):
        self.bind("<Control-o>", lambda event: self.open_xml())
        self.bind("<Control-s>", lambda event: self.save_xml())
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def open_xml(self):
        selected_path = filedialog.askopenfilename(
            title="打开 XML 配置",
            filetypes=(("XML 文件", "*.xml"), ("所有文件", "*.*")),
        )
        if selected_path:
            self.load_xml(Path(selected_path))

    def load_xml(self, path):
        try:
            tree = ET.parse(path)
        except (ET.ParseError, OSError) as error:
            messagebox.showerror("打开失败", f"无法读取 XML:\n{error}")
            return

        self.xml_path = Path(path)
        self.xml_root = tree.getroot()
        self.dirty = False
        self.search_matches = []
        self.search_index = -1
        self.populate_wifi_tree()
        self.title(f"XML 配置编辑器 - {self.xml_path.name}")
        if self.wlan_container is None:
            messagebox.showwarning("没有 WiFi 配置", "XML 中未找到 LANDevice/WLANConfiguration。")
            self.status_value.set("未找到 WLANConfiguration")
            return
        declared_count = self.wlan_container.get("NumberOfInstances", "未声明")
        actual_count = len(self.wlan_configurations)
        self.status_value.set(f"WLAN 配置：声明 {declared_count} 个，实际读取 {actual_count} 个")

    def find_wifi_configurations(self):
        self.wlan_container = None
        self.wlan_configurations = []
        for lan_device in self.xml_root.iter("LANDevice"):
            for lan_instance in lan_device.findall("LANDeviceInstance"):
                wlan_container = lan_instance.find("WLANConfiguration")
                if wlan_container is not None:
                    self.wlan_container = wlan_container
                    self.wlan_configurations = wlan_container.findall("WLANConfigurationInstance")
                    return

    def populate_wifi_tree(self):
        self.find_wifi_configurations()
        self.element_tree.delete(*self.element_tree.get_children())
        self.tree_nodes.clear()
        if self.wlan_container is None:
            return
        declared_count = self.wlan_container.get("NumberOfInstances", "未声明")
        group_id = self.element_tree.insert(
            "",
            "end",
            text=f"WLANConfiguration（声明 {declared_count} 个，实际 {len(self.wlan_configurations)} 个）",
            open=True,
        )
        for element in self.wlan_configurations:
            element_id = self.element_tree.insert(group_id, "end", text=self.wlan_text(element))
            self.tree_nodes[element_id] = element
        if self.wlan_configurations:
            first_id = next(iter(self.tree_nodes))
            self.element_tree.selection_set(first_id)

    @staticmethod
    def wlan_text(element):
        instance_id = element.get("InstanceID", "?")
        name = element.get("Name", "")
        ssid = element.get("SSID", "")
        enabled = element.get("Enable", "")
        band = element.get("X_HW_RFBand", "")
        return f"实例 {instance_id} | {name} | SSID: {ssid} | Enable: {enabled} | {band}"

    @staticmethod
    def node_text(element):
        text = (element.text or "").strip().replace("\n", " ")
        suffix = f" = {text[:50]}" if text else ""
        return f"<{element.tag}>{suffix}"

    def on_tree_select(self, event=None):
        selection = self.element_tree.selection()
        if not selection:
            return
        element = self.tree_nodes.get(selection[0])
        if element is None:
            return
        self.selected_element = element
        self.element_label.configure(text=f"<{element.tag}>")
        self.ssid_value.set(element.get("SSID", ""))
        self.standard_value.set(element.get("Standard", ""))
        self.ht20_value.set(element.get("X_HW_HT20", ""))
        self.bandwidth_value.set(element.get("X_HW_OperatingChannelBandwidth", ""))
        self.channel_value.set(element.get("Channel", ""))
        password_node = element.find("./PreSharedKey/PreSharedKeyInstance")
        self.password_value.set(password_node.get("PreSharedKey", "") if password_node is not None else "")
        self.attribute_table.delete(*self.attribute_table.get_children())
        self.attribute_values.clear()
        for name, value in element.attrib.items():
            row_id = self.attribute_table.insert("", "end", values=(name, value))
            self.attribute_values[row_id] = name
        self.attribute_edit.delete(0, tk.END)

    def apply_wifi_settings(self):
        if self.selected_element is None:
            return

        element = self.selected_element
        standard = self.standard_value.get().strip()
        if standard:
            # 设备配置要求这两个字段保持一致，否则标准可能显示与实际能力不符。
            element.set("Standard", standard)
            element.set("X_HW_Standard", standard)
        element.set("SSID", self.ssid_value.get())
        element.set("X_HW_HT20", self.ht20_value.get().strip())
        element.set("X_HW_OperatingChannelBandwidth", self.bandwidth_value.get().strip())
        element.set("Channel", self.channel_value.get().strip())

        password_node = element.find("./PreSharedKey/PreSharedKeyInstance")
        if password_node is not None:
            password_node.set("PreSharedKey", self.password_value.get())
        else:
            messagebox.showwarning("密码未写入", "当前 WLAN 配置没有 PreSharedKeyInstance 节点。")

        self.refresh_attribute_table()
        self.refresh_selected_node()
        self.dirty = True
        self.status_value.set("WiFi 设置已修改，尚未保存")

    def refresh_attribute_table(self):
        if self.selected_element is None:
            return
        self.attribute_table.delete(*self.attribute_table.get_children())
        self.attribute_values.clear()
        for name, value in self.selected_element.attrib.items():
            row_id = self.attribute_table.insert("", "end", values=(name, value))
            self.attribute_values[row_id] = name

    def begin_attribute_edit(self, event=None):
        row_id = self.attribute_table.identify_row(event.y) if event else None
        if not row_id:
            return
        self.attribute_table.selection_set(row_id)
        values = self.attribute_table.item(row_id, "values")
        self.attribute_edit.delete(0, tk.END)
        if len(values) > 1:
            self.attribute_edit.insert(0, values[1])
        self.attribute_edit.focus_set()

    def apply_attribute(self):
        if self.selected_element is None:
            return
        selection = self.attribute_table.selection()
        if not selection:
            return
        row_id = selection[0]
        attribute_name = self.attribute_values.get(row_id)
        if not attribute_name:
            return
        new_value = self.attribute_edit.get()
        self.selected_element.set(attribute_name, new_value)
        self.attribute_table.item(row_id, values=(attribute_name, new_value))
        self.refresh_selected_node()
        self.dirty = True
        self.status_value.set("有未保存修改")

    def refresh_selected_node(self):
        selection = self.element_tree.selection()
        if selection and self.selected_element is not None:
            self.element_tree.item(selection[0], text=self.wlan_text(self.selected_element))

    def search(self):
        query = self.search_value.get().strip().lower()
        if not query or self.xml_root is None:
            return
        self.search_matches = []
        for element_id, element in self.tree_nodes.items():
            searchable = [element.tag, element.text or ""]
            searchable.extend(f"{name}={value}" for name, value in element.attrib.items())
            if query in " ".join(searchable).lower():
                self.search_matches.append(element_id)
        if not self.search_matches:
            messagebox.showinfo("搜索", "没有找到匹配项")
            return
        self.search_index = (self.search_index + 1) % len(self.search_matches)
        match_id = self.search_matches[self.search_index]
        self.open_tree_path(match_id)
        self.status_value.set(f"WLAN 配置匹配 {self.search_index + 1}/{len(self.search_matches)} 项")

    def open_tree_path(self, item_id):
        ancestors = []
        current_id = item_id
        while current_id:
            ancestors.append(current_id)
            current_id = self.element_tree.parent(current_id)
        for ancestor_id in reversed(ancestors):
            self.element_tree.item(ancestor_id, open=True)
        self.element_tree.selection_set(item_id)
        self.element_tree.see(item_id)

    def save_xml(self):
        if self.xml_path is None or self.xml_root is None:
            return self.save_xml_as()
        return self.write_xml(self.xml_path)

    def save_xml_as(self):
        if self.xml_root is None:
            return False
        selected_path = filedialog.asksaveasfilename(
            title="另存 XML 配置",
            defaultextension=".xml",
            initialfile=self.xml_path.name if self.xml_path else "config.xml",
            filetypes=(("XML 文件", "*.xml"), ("所有文件", "*.*")),
        )
        return self.write_xml(Path(selected_path)) if selected_path else False

    def write_xml(self, path):
        try:
            backup_path = path.with_suffix(path.suffix + ".bak")
            if path.exists():
                backup_path.write_bytes(path.read_bytes())
            output_root = copy.deepcopy(self.xml_root)
            self.indent_xml(output_root)
            output_tree = ET.ElementTree(output_root)
            output_tree.write(path, encoding="utf-8", xml_declaration=True)
            ET.parse(path)
        except (OSError, ET.ParseError) as error:
            messagebox.showerror("保存失败", f"保存或校验 XML 失败:\n{error}")
            return False

        self.xml_path = path
        self.dirty = False
        self.title(f"XML 配置编辑器 - {path.name}")
        self.status_value.set(f"已保存，备份: {path.name}.bak")
        return True

    @staticmethod
    def indent_xml(element, level=0):
        indentation = "\n" + "    " * level
        child_indentation = "\n" + "    " * (level + 1)
        if len(element):
            if not element.text or not element.text.strip():
                element.text = child_indentation
            for child in element:
                XmlConfigEditor.indent_xml(child, level + 1)
                if not child.tail or not child.tail.strip():
                    child.tail = child_indentation
            if not element[-1].tail or not element[-1].tail.strip():
                element[-1].tail = indentation
        elif level and (not element.tail or not element.tail.strip()):
            element.tail = indentation

    def close_window(self):
        if self.dirty and not messagebox.askyesno("未保存修改", "配置有未保存修改，确定退出吗？"):
            return
        self.destroy()


if __name__ == "__main__":
    XmlConfigEditor().mainloop()