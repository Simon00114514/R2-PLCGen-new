import xml.etree.ElementTree as ET
import os
import sys

namespaces = {
            '': 'http://www.plcopen.org/xml/tc6_0201',  # 默认命名空间
            'ns1': 'http://www.plcopen.org/xml/tc6_0201',  # 可以根据需要添加其他命名空间
            'xhtml': 'http://www.w3.org/1999/xhtml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }
def start_redirect(output_file_path):
    global original_stdout
    original_stdout = sys.stdout
    sys.stdout = open(output_file_path, 'w')

def stop_redirect():
    global original_stdout
    sys.stdout.close()
    sys.stdout = original_stdout
def parse_type(type_tag):
    if type_tag is None:
        return "UNKNOWN"
    # 获取变量的基本类型
    base_type = type_tag.find("*", namespaces)
    if base_type is not None:
        type_name = base_type.tag.split("}")[-1]
        if type_name == "pointer":
            pointer_type = base_type.find("baseType/*", namespaces)
            if pointer_type is not None:
                return f"POINTER TO {pointer_type.tag.split('}')[-1]}"
        elif type_name == "array":
            dimensions = [
                f"{dim.get('lower')}..{dim.get('upper')}"
                for dim in base_type.findall("dimension", namespaces)
            ]
            base_array_type = base_type.find("baseType/*", namespaces)
            if base_array_type is not None:
                return f"array[{','.join(dimensions)}] of {base_array_type.tag.split('}')[-1]}"
        elif type_name == "derived":
            return type_tag.find("derived", namespaces).get("name")
        elif type_name == "string":
            return "WSTRING"
        else:
            return type_name
    return "UNKNOWN"

# 初始值解析函数
def parse_initial_value(var_tag):
    initial_value_tag = var_tag.find("initialValue", namespaces)
    if initial_value_tag is not None:
        simple_value = initial_value_tag.find("simpleValue", namespaces)
        if simple_value is not None:
            return f" := {simple_value.get('value')}"
        array_value = initial_value_tag.find("arrayValue", namespaces)
        if array_value is not None:
            values = []
            for value in array_value.findall("value", namespaces):
                repetition = value.get("repetitionValue", 1)
                simple_value = value.find("simpleValue", namespaces)
                if simple_value is not None:
                    values.extend([simple_value.get("value")] * int(repetition))
            return f" := [{','.join(values)}]"
    return ""

def trans_xml(file_path):
    file_name = os.path.basename(file_path)
    # 去掉文件后缀并添加.scl 后缀
    scl_file_name = os.path.splitext(file_name)[0] + '.scl'
    output_dir = os.path.dirname(file_path)
    output_path = os.path.join(output_dir, scl_file_name)
    start_redirect(output_path)

    tree = ET.parse(file_path)  # 直接从文件解析
    root = tree.getroot()  # 获取根节点

    namespaces = {
            '': 'http://www.plcopen.org/xml/tc6_0201',  # 默认命名空间
            'ns1': 'http://www.plcopen.org/xml/tc6_0201',
            'xhtml': 'http://www.w3.org/1999/xhtml',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

    # 生成输出
    for global_vars in root.findall(".//globalVars", namespaces):
        if len(global_vars.findall("variable", namespaces)) > 0:
            print("VAR_GLOBAL")

            for variable in global_vars.findall("variable", namespaces):
                var_name = variable.get("name")
                var_type = "unknown"
                initial_value = ""  # 默认初始值为空

                # 处理变量类型
                type_tag = variable.find("type", namespaces)
                if type_tag is not None:
                    # 基本类型处理（如 INT, REAL, TIME, DATE）
                    base_type = type_tag.find("*", namespaces)
                    if base_type is not None:
                        var_type = base_type.tag.split('}')[-1]

                    # 自定义类型（<derived>）
                    derived_type = type_tag.find("derived", namespaces)
                    if derived_type is not None:
                        var_type = derived_type.get("name")

                    # 数组类型处理
                    array_tag = type_tag.find("array", namespaces)
                    if array_tag is not None:
                        dimensions = []
                        for dimension in array_tag.findall("dimension", namespaces):
                            lower = dimension.get("lower")
                            upper = dimension.get("upper")
                            dimensions.append(f"{lower}..{upper}")
                        base_type = array_tag.find("baseType", namespaces).find("*").tag.split('}')[-1]
                        var_type = f"array[{','.join(dimensions)}] of {base_type}"

                # 获取初始值
                initial_value_tag = variable.find("initialValue", namespaces)
                if initial_value_tag is not None:
                    simple_value = initial_value_tag.find(".//simpleValue", namespaces)
                    if simple_value is not None:
                        initial_value = f" := {simple_value.get('value')};"

                    # 数组值初始值
                    array_value = initial_value_tag.find(".//arrayValue", namespaces)
                    if array_value is not None:
                        values = []
                        for value_tag in array_value.findall("value", namespaces):
                            repetition = int(value_tag.get("repetitionValue", 1))
                            value = value_tag.find("simpleValue", namespaces).get("value")
                            values.extend([value] * repetition)
                        initial_value = f" := [{','.join(values)}];"

                # 如果没有初始值，确保有分号
                if not initial_value:
                    initial_value = ";"

                # 输出变量
                print(f"\t{var_name} : {var_type}{initial_value}")

            print("END_VAR")

    # 获取所有数据类型
    data_types = root.findall(".//dataType", namespaces)

    # 生成输出
    for data_type in data_types:
        name = data_type.get("name")
        print(f"TYPE \n\t{name}: STRUCT")

        # 查找struct内的所有变量
        struct = data_type.find(".//struct", namespaces)
        if struct is not None:
            for variable in struct.findall("variable", namespaces):
                var_name = variable.get("name")
                var_type = "unknown"
                initial_value = ""  # 默认初始值为空

                # 处理基本类型、数组、自定义类型
                type_tag = variable.find("type", namespaces)
                if type_tag is not None:
                    # 基本类型处理（如 INT, DINT）
                    base_type = type_tag.find("*", namespaces)
                    if base_type is not None:
                        var_type = base_type.tag.split('}')[-1]

                    # 自定义类型（<derived>）
                    derived_type = type_tag.find("derived", namespaces)
                    if derived_type is not None:
                        var_type = derived_type.get("name")

                    # 数组类型处理
                    array_tag = type_tag.find("array", namespaces)
                    if array_tag is not None:
                        dimensions = []
                        for dimension in array_tag.findall("dimension", namespaces):
                            lower = dimension.get("lower")
                            upper = dimension.get("upper")
                            dimensions.append(f"{lower}..{upper}")
                        base_type = array_tag.find("baseType", namespaces).find("*", namespaces).tag.split('}')[-1]
                        var_type = f"array[{','.join(dimensions)}] of {base_type}"

                # 获取初始值
                initial_value_tag = variable.find("initialValue", namespaces)
                if initial_value_tag is not None:
                    # 简单值初始值
                    simple_value = initial_value_tag.find(".//simpleValue", namespaces)
                    if simple_value is not None:
                        initial_value = f" := {simple_value.get('value')};"

                    # 数组值初始值
                    array_value = initial_value_tag.find(".//arrayValue", namespaces)
                    if array_value is not None:
                        values = []
                        for value_tag in array_value.findall("value", namespaces):
                            repetition = int(value_tag.get("repetitionValue", 1))
                            value = value_tag.find("simpleValue", namespaces).get("value")
                            values.extend([value] * repetition)
                        initial_value = f" := [{','.join(values)}];"

                # 如果没有初始值，确保有分号
                if not initial_value:
                    initial_value = ";"

                # 输出变量
                print(f"\t{var_name} : {var_type}{initial_value}")

        print("\tEND_STRUCT;")
        print("END_TYPE")

    # 查找所有的 <pou> 元素
    for pou in root.findall(".//pou", namespaces):
        pou_name = pou.get("name")
        pou_type = pou.get("pouType")
        pou_return_type = None
        if pou_type == "function":
            interface = pou.find("interface", namespaces)
            if interface is not None:
                return_type_tag = interface.find("returnType", namespaces)
                if return_type_tag is not None:
                    pou_return_type = parse_type(return_type_tag)

        # 输出 POU 名称和类型
        if pou_type == "program":
            print(f"{pou_type.upper()} {pou_name}")
        elif pou_type == "functionBlock":
            print(f"FUNCTION_BLOCK {pou_name}")
        elif pou_type == "function":
            print(f"{pou_type.upper()} {pou_name} : {pou_return_type}")
        # 解析接口部分
        interface = pou.find("interface", namespaces)
        if interface is not None:
            for var_section in ["localVars", "inputVars", "outputVars", "inOutVars"]:
                section = interface.find(f"{var_section}", namespaces)
                if section is not None:
                    section_name = {
                        "localVars": "VAR",
                        "inputVars": "VAR_INPUT",
                        "outputVars": "VAR_OUTPUT",
                        "inOutVars": "VAR_IN_OUT"
                    }[var_section]
                    print(f"\t{section_name}")
                    for variable in section.findall("variable", namespaces):
                        var_name = variable.get("name")
                        var_type = parse_type(variable.find("type", namespaces))
                        initial_value = parse_initial_value(variable)
                        print(f"\t\t{var_name} : {var_type}{initial_value};")
                    print("\tEND_VAR")

        # 解析主体部分
        body = pou.find("body/ST/xhtml:p", namespaces)
        if body is not None:
            print()
            body_text = body.text.strip()

            # 去掉多余的换行符，并确保至少保留一个空行
            body_lines = body_text.splitlines()

            # 使用一个标志来检查是否遇到多个连续的空行
            filtered_lines = []
            empty_line_count = 0  # 记录空行的数量

            for line in body_lines:
                stripped_line = line.strip()
                if stripped_line == "":
                    empty_line_count += 1
                    # 如果已经有一个空行，则跳过这个空行
                    if empty_line_count > 1:
                        filtered_lines.append(line)
                else:
                    filtered_lines.append(line)
                    empty_line_count = 0  # 重置空行计数

            # 重新连接并打印主体内容
            formatted_body = "\n\t".join(filtered_lines)
            print("\t" + formatted_body)


            #print("\t" + body_text.replace("\n", "\n\t"))
        if pou_type == "functionBlock":
            print(f"END_FUNCTION_BLOCK")
        else:
            print(f"END_{pou_type.upper()}")

    stop_redirect()