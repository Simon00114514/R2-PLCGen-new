#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#


import os
import wx
import wx.html2
import wx.grid
import xml_translate
import sys


class PluginDialog(wx.Dialog):
    def __init__(self, parent, info):
        title = "Formal Verif Plugin"
        wx.Dialog.__init__(self, parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetSize((800, 600))  # 修改尺寸以适应两个选项卡
        self.SetMinSize((800, 600))
        self.SetMaxSize((1000, 1000))
        self.info = info
        self.html_file_path = ''

        if parent and parent.GetIcon():
            self.SetIcon(parent.GetIcon())

        # 创建 Notebook 控件
        self.notebook = wx.Notebook(self, style=wx.NB_TOP)
        self.notebook.SetMinSize((800, 600))
        self.notebook.SetSize((800, 600))

        # 创建第一个选项卡（Verifcase.vc3）
        self.verifcase_panel = wx.ScrolledWindow(self.notebook)
        self.notebook.AddPage(self.verifcase_panel, "Verifcase")

        # 在第一个选项卡中添加控件
        metadata_label = wx.StaticText(self.verifcase_panel, label="Metadata")
        id_label = wx.StaticText(self.verifcase_panel, label="ID")
        self.id_text = wx.TextCtrl(self.verifcase_panel)
        name_label = wx.StaticText(self.verifcase_panel, label="NAME")
        self.name_text = wx.TextCtrl(self.verifcase_panel)
        description_label = wx.StaticText(self.verifcase_panel, label="DESCRIPTION")
        self.description_text = wx.TextCtrl(self.verifcase_panel)

        sourcefile_label = wx.StaticText(self.verifcase_panel, label="SourceFile")
        sourcefiles_list = wx.ListBox(self.verifcase_panel, pos=(20, 20), size=(350, 100))
        self.sourcefiles_list = sourcefiles_list
        translate_file_button = wx.Button(self.verifcase_panel, label="Translate XML File")
        translate_file_button.Bind(wx.EVT_BUTTON, self.on_translate_file_button)
        add_file_button = wx.Button(self.verifcase_panel, label="Add File")
        add_file_button.Bind(wx.EVT_BUTTON, self.on_add_file_button)
        # sourcefiles_list.InsertColumn(0, "Sourcefiles", width=400)

        entry_block_label = wx.StaticText(self.verifcase_panel, label="Entry_Block")
        self.entry_block_text = wx.TextCtrl(self.verifcase_panel)

        verifymessage_label = wx.StaticText(self.verifcase_panel, label="VerifMessage")
        self.pattern_choice = wx.Choice(self.verifcase_panel, choices=[
            "If {1} is true at the end of the PLC cycle, then {2} should always be true at the end of the same cycle.",
            "{1} is always true at the end of the PLC cycle.",
            "{1} is impossible at the end of the PLC cycle.",
            "If {1} is true at the beginning of the PLC cycle, then {2} is always true at the end of the same cycle.",
            "If {1} is true at the end of cycle N and {2} is true at the end of cycle N+1, then {3} is always true at the end of cycle N+1.",
            "It is possible to have {1} at the end of a cycle.",
            "Any time it is possible to have eventually {1} at the end of a cycle.",
            "If {1} is true at the end of a cycle, {2} was true at the end of an earlier cycle."
        ], pos=(100, 10))
        self.parameter_texts = []
        self.pattern_choice.Bind(wx.EVT_CHOICE, self.on_update_parameters)
        self.pattern_choice.SetSelection(0)
        self.pattern_choice.Bind(wx.EVT_MOUSEWHEEL, self.on_choice_mouse_wheel)

        advance_setting_label = wx.StaticText(self.verifcase_panel, label="Advanced setting(BOOL or TYPE#VALUE)")
        add_button = wx.Button(self.verifcase_panel, label="Add Row")
        add_button.Bind(wx.EVT_BUTTON, self.on_add_row)
        self.grid = wx.grid.Grid(self.verifcase_panel)
        self.grid.CreateGrid(3, 4)
        self.grid.SetColLabelValue(0, 'Variable Name')
        self.grid.SetColLabelValue(1, 'Initial Value')
        self.grid.SetColLabelValue(2, 'Bound Low')
        self.grid.SetColLabelValue(3, 'Bound High')
        self.grid.SetColSize(0, 150)
        self.grid.SetColSize(1, 150)
        self.grid.SetColSize(2, 150)
        self.grid.SetColSize(3, 150)
        self.grid.EnableEditing(True)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.on_cell_changed)

        verif_button = wx.Button(self.verifcase_panel, label="Go Verif")
        verif_button.SetMinSize((200, 50))
        verif_button.SetForegroundColour(wx.Colour(205, 92, 92))
        verif_button.SetBackgroundColour(wx.Colour(30, 144, 255))
        verif_button.Bind(wx.EVT_BUTTON, self.get_verif)
        report_button = wx.Button(self.verifcase_panel, label="Open Report")
        report_button.SetMinSize((200, 50))
        report_button.Bind(wx.EVT_BUTTON, self.go_page2)

        close = wx.Button(self.verifcase_panel, id=wx.ID_CANCEL, label="&Close")
        close.Bind(wx.EVT_BUTTON, self.on_close)

        # 修正布局
        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(close, flag=wx.CENTER | wx.RIGHT, border=5)

        # 元数据部分布局
        metadata_sizer = wx.BoxSizer(wx.VERTICAL)
        metadata_sizer.Add(metadata_label, flag=wx.TOP | wx.LEFT, border=10)
        fgs = wx.FlexGridSizer(3, 2, 9, 25)
        fgs.AddGrowableCol(1, 1)
        fgs.AddGrowableRow(2, 1)
        fgs.AddMany([(id_label), (self.id_text, 1, wx.EXPAND), (name_label),
                     (self.name_text, 1, wx.EXPAND), (description_label, 1, wx.EXPAND),
                     (self.description_text, 1, wx.EXPAND)])
        metadata_sizer.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)

        # 文件部分布局
        file_sizer = wx.BoxSizer(wx.VERTICAL)
        file_sizer.Add(sourcefile_label, flag=wx.TOP | wx.LEFT, border=10)
        file_sizer.Add(sourcefiles_list, flag=wx.EXPAND | wx.ALL, border=10)
        file_sizer.Add(translate_file_button, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=10)
        file_sizer.Add(add_file_button, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, border=10)

        # 验证进入
        entry_sizer = wx.BoxSizer(wx.HORIZONTAL)
        entry_sizer.Add(entry_block_label, flag=wx.EXPAND | wx.ALL, border=10)
        entry_sizer.Add(self.entry_block_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        # 验证消息部分布局
        verify_sizer = wx.BoxSizer(wx.VERTICAL)
        self.verify_sizer = verify_sizer
        self.verify_sizer.Add(verifymessage_label, flag=wx.TOP | wx.LEFT, border=10)
        self.verify_sizer.Add(self.pattern_choice, flag=wx.TOP | wx.LEFT, border=10)
        self.on_update_parameters(None)

        # 特殊定义部分布局
        advance_sizer = wx.BoxSizer(wx.VERTICAL)
        advance_top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        advance_top_sizer.Add(advance_setting_label, flag=wx.TOP | wx.LEFT, border=10)
        advance_top_sizer.Add(add_button, flag=wx.TOP | wx.RIGHT, border=10)
        advance_sizer.Add(advance_top_sizer)
        advance_sizer.Add(self.grid, flag=wx.EXPAND | wx.ALL, border=10)

        # 验证布局
        verif_button_sizer = wx.BoxSizer(wx.VERTICAL)
        verif_button_sizer.Add(verif_button, flag=wx.TOP | wx.LEFT, border=10)
        verif_button_sizer.Add(report_button, flag=wx.TOP | wx.LEFT, border=10)

        # 整体布局
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(metadata_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        main_sizer.Add(file_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        main_sizer.Add(entry_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        main_sizer.Add(self.verify_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        main_sizer.Add(advance_sizer, flag=wx.EXPAND | wx.ALL, border=10)
        main_sizer.Add(verif_button_sizer, flag=wx.CENTER | wx.BOTTOM, border=10)
        main_sizer.Add(btnSizer, flag=wx.CENTER | wx.BOTTOM, border=10)

        # 设置 sizer 到 verifcase_panel
        self.verifcase_panel.SetSizer(main_sizer)

        # 设置虚拟大小，确保能滚动
        self.verifcase_panel.SetVirtualSize(self.verifcase_panel.GetBestSize())

        # 设置滚动步长
        self.verifcase_panel.SetScrollRate(10, 10)

        # 创建第二个选项卡（Verifreport.html）
        self.verifreport_panel = wx.ScrolledWindow(self.notebook)
        self.notebook.AddPage(self.verifreport_panel, "Verifreport")

        # 在第二个选项卡中添加一个 web 视图控件来显示 HTML 文件
        self.web_view = wx.html2.WebView.New(self.verifreport_panel)
        # 加载 HTML 文件
        self.web_view.LoadURL(self.html_file_path)

        self.web_view.SetSize(self.verifreport_panel.GetSize())

        web_sizer = wx.BoxSizer(wx.VERTICAL)
        self.verifreport_panel.SetSizer(web_sizer)

        # 设置布局
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)
        self.Layout()
        self.Fit()
        self.Centre()
        self.Show(True)

    def on_translate_file_button(self, event):
        # 创建文件对话框
        file_dialog = wx.FileDialog(self, "选择文件",
                                    wildcard="XML files|*.xml|All files (*.*)|*.*",
                                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        # 判断用户是否选择了文件
        if file_dialog.ShowModal() == wx.ID_OK:
            # 获取文件路径
            file_path = file_dialog.GetPath()
            # 将文件路径添加到列表框中
            xml_translate.trans_xml(file_path)

        else:
            print("Dialog was cancelled by the user")

        # 关闭文件对话框
        file_dialog.Destroy()

    def on_add_file_button(self, event):
        # 创建文件对话框
        file_dialog = wx.FileDialog(self, "选择文件",
                                    wildcard="ST and SCL files (*.st;*.scl)|*.st;*.scl|ST files (*.st)|*.st|SCL files (*.scl)|*.scl|All files (*.*)|*.*",
                                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        # 判断用户是否选择了文件
        if file_dialog.ShowModal() == wx.ID_OK:
            # 获取文件路径
            file_path = file_dialog.GetPath()
            # 将文件路径添加到列表框中
            self.sourcefiles_list.Append(file_path)

        else:
            print("Dialog was cancelled by the user")

        # 关闭文件对话框
        file_dialog.Destroy()

    def on_update_parameters(self, event):
        # 清空现有的 parameter_texts
        for text_ctrl in self.parameter_texts:
            text_ctrl.Destroy()
        self.parameter_texts.clear()

        # 获取选择的模式
        self.selected_pattern = self.pattern_choice.GetStringSelection()

        # 根据选择的模式创建对应数量的 TextCtrl
        if self.selected_pattern == "{1} is always true at the end of the PLC cycle." or self.selected_pattern == "{1} is impossible at the end of the PLC cycle." or self.selected_pattern == "It is possible to have {1} at the end of a cycle." or self.selected_pattern == "Any time it is possible to have eventually {1} at the end of a cycle.":
            self.create_parameter_texts(1)
        elif self.selected_pattern == "If {1} is true at the end of the PLC cycle, then {2} should always be true at the end of the same cycle." or self.selected_pattern == "If {1} is true at the beginning of the PLC cycle, then {2} is always true at the end of the same cycle." or self.selected_pattern == "If {1} is true at the end of a cycle, {2} was true at the end of an earlier cycle.":
            self.create_parameter_texts(2)
        elif self.selected_pattern == "If {1} is true at the end of cycle N and {2} is true at the end of cycle N+1, then {3} is always true at the end of cycle N+1.":
            self.create_parameter_texts(3)

    def create_parameter_texts(self, count):
        # 创建指定数量的 TextCtrl
        for i in range(count):
            param_text = wx.TextCtrl(self.verifcase_panel, pos=(100, 70 + i * 30))
            self.parameter_texts.append(param_text)

            self.verify_sizer.Add(param_text, flag=wx.EXPAND | wx.ALL, border=5)

        self.verifcase_panel.Layout()

    def on_choice_mouse_wheel(self, event):
        # 阻止Choice控件的滚动行为
        event.Skip(False)

    def on_add_row(self, event):
        current_row_count = self.grid.GetNumberRows()
        self.grid.AppendRows(1)  # 增加1行

        self.grid.SetCellValue(current_row_count, 0, f'Variable {current_row_count + 1}')
        self.grid.SetCellValue(current_row_count, 1, 'true')

    def on_cell_changed(self, event):
        row = event.GetRow()
        col = event.GetCol()
        new_value = self.grid.GetCellValue(row, col)

        if col == 0:
            print(f"Variable Name updated: {new_value} (Row {row})")
        elif col == 1:
            print(f"Initial Value updated: {new_value} (Row {row})")

        # 允许事件继续处理
        event.Skip()

    def on_close(self, event):
        self.Destroy()
        sys.exit(0)

    def Close(self, force=False):
        self.Destroy()
        sys.exit(0)

    def go_page2(self, event):
        # 跳转到第二个页面
        # self.html_file_path = 'D:\PLCverif\workspace\example\output\example.report.html'
        self.web_view.LoadURL(self.html_file_path)
        self.notebook.SetSelection(1)

    def get_verif(self, event):
        # 将st传输给nusmv  获取用户的需要验证的信息
        name_param = ' -name=' + self.name_text.GetValue()
        id_param = ' -id=' + self.id_text.GetValue()
        description_param = ' -description=' + '"' + self.description_text.GetValue() + '"'

        source_file_param = ''
        for i in range(self.sourcefiles_list.GetCount()):
            source_file_param = source_file_param + ' -sourcefiles.' + str(i+1) + '=' + self.sourcefiles_list.GetString(i)

        entry_param = ' -lf.entry=' + self.entry_block_text.GetValue()

        if self.selected_pattern == "{1} is always true at the end of the PLC cycle.":
            pattern = "pattern-invariant"
        elif self.selected_pattern == "{1} is impossible at the end of the PLC cycle.":
            pattern = "pattern-forbidden"
        elif self.selected_pattern == "It is possible to have {1} at the end of a cycle.":
            pattern = "pattern-reachability"
        elif self.selected_pattern == "Any time it is possible to have eventually {1} at the end of a cycle.":
            pattern = "pattern-repeatability"
        elif self.selected_pattern == "If {1} is true at the end of the PLC cycle, then {2} should always be true at the end of the same cycle.":
            pattern = "pattern-implication"
        elif self.selected_pattern == "If {1} is true at the beginning of the PLC cycle, then {2} is always true at the end of the same cycle.":
            pattern = "pattern-statechange-duringcycle"
        elif self.selected_pattern == "If {1} is true at the end of a cycle, {2} was true at the end of an earlier cycle.":
            pattern = "pattern-leadsto"
        elif self.selected_pattern == "If {1} is true at the end of cycle N and {2} is true at the end of cycle N+1, then {3} is always true at the end of cycle N+1.":
            pattern = "pattern-statechange-betweencycles"

        pattern_params = []
        for i in range(len(self.parameter_texts)):
            param_text = self.parameter_texts[i]
            text = param_text.GetValue()
            pattern_params.append(text)

        pattern_param = ' -job.req.pattern_id=' + pattern
        if pattern == 'pattern-statechange-betweencycles':
            pattern_param = pattern_param + ' -job.req.pattern_params.1="' + pattern_params[
                0] + '"' + ' -job.req.pattern_params.2="' + pattern_params[1] + '"' + ' -job.req.pattern_params.3="' + \
                            pattern_params[2] + '"'
        elif pattern == 'pattern-implication' or pattern == 'pattern-statechange-duringcycle' or pattern == 'pattern-leadsto':
            pattern_param = pattern_param + ' -job.req.pattern_params.1="' + pattern_params[
                0] + '"' + ' -job.req.pattern_params.2="' + pattern_params[1] + '"'
        else:
            pattern_param = pattern_param + ' -job.req.pattern_params.1="' + pattern_params[0] + '"'

        binding_data_param = ' '
        # 获取行数
        num_rows = self.grid.GetNumberRows()
        # 获取每列的数据
        for row in range(num_rows):
            if self.grid.GetCellValue(row, 1) != '':
                binding_data_param = binding_data_param + ' -job.req.bindings.variable.' + str(
                    row) + '=' + self.grid.GetCellValue(row, 0)
                binding_data_param = binding_data_param + ' -job.req.bindings.value.' + str(
                    row) + '=' + self.grid.GetCellValue(row, 1)
            if self.grid.GetCellValue(row, 2) != '':
                binding_data_param = binding_data_param + ' -job.req.lowerBounds.variable.' + str(
                    row) + '=' + self.grid.GetCellValue(row, 0)
                binding_data_param = binding_data_param + ' -job.req.lowerBounds.value.' + str(
                    row) + '=' + self.grid.GetCellValue(row, 2)
            if self.grid.GetCellValue(row, 3) != '':
                binding_data_param = binding_data_param + ' -job.req.upperBounds.variable.' + str(
                    row) + '=' + self.grid.GetCellValue(row, 0)
                binding_data_param = binding_data_param + ' -job.req.upperBounds.value.' + str(
                    row) + '=' + self.grid.GetCellValue(row, 3)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        plcverif = os.path.join(current_dir, "PLCverif_cli", "eclipsec.exe")
        cli_set_path = os.path.join(current_dir, "PLCverif_cli", "cli_set.txt")
        html_file_dir = os.path.join(current_dir, "PLCverif_cli", "output")
        os.system(
                 plcverif + " " + cli_set_path + name_param + ' ' + id_param + ' ' + description_param + ' ' +
                 source_file_param + ' ' + entry_param + pattern_param + binding_data_param)

        self.html_file_path = html_file_dir +"\\"+ self.id_text.GetValue() + '.report.html'
        print(self.html_file_path)

def ShowPluginDialog(parent, info):
    PluginDialog(parent, info)

if __name__ == "__main__":
    app = wx.App(False)
    info = {}  # 你可以根据需要添加信息
    dialog = PluginDialog(None, info)
    app.MainLoop()