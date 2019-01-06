#! coding:utf-8

import string


class Session(object):
    def __init__(self, s):
        self.key = s
        self.define_data = []
        self.notdefine_data = []
        self.cur_state = 2


class TupleData(object):
    def __init__(self):
        self.data = []


STRING_PLACEHOLDER = '%%'
CHAR_PLACEHOLDER = '@@'
IF_DEF = 'ifdef'
IF_NDEF = 'ifndef'
END_IF = 'endif'
ELSE = 'else'
DEFINE = 'define'
UNDEF = 'undef'
NONE = 'None'

ESCAPE_MAP = {
    '\\\\': '\\',
    '\\f': '\f',
    '\\n': '\n',
    '\\t': '\t',
    '\\r': '\r',
    '\\a': '\a',
    '\\b': '\b',
    '\\v': '\v',
    '\\\'': '\'',
    '\\\"': '\"',
}
REVOKE_ESCAPE_MAP = {v: k for k, v in ESCAPE_MAP.items()}


class PyMacroParser(object):
    """
    读取 .cpp文件中的宏定义，解析出当前所有的可用的宏定义

    Attributes:
        _pre_define_macros:存储从python外部增加的预定义宏
        _cpp_data:存储从cpp读取的所有宏数据

    """

    def __init__(self):
        self._pre_define_macros = []
        self._cpp_data = None

    def load(self, f):
        """ 读取cpp文件，去除注释和空行 将数据存储到Session数据结构中 """
        # self._pre_define_macros = []
        self._cpp_data = None
        self._dump_dict = {}

        try:
            context = self._load_and_reomve_notes(f)
        except:
            raise
        root = Session('root')
        stack = []
        stack.append(root)
        index = 0
        while len(stack) > 0 and index < len(context):
            node = stack.pop()
            data = self._split_string(context[index][0])
            while data[0] != END_IF and index < len(context):
                if data[0] == DEFINE or data[0] == UNDEF:
                    if node.cur_state == 1:
                        node.define_data.append((data[1], (data[2], context[index][1])))
                    else:
                        node.notdefine_data.append((data[1], (data[2], context[index][1])))
                elif data[0] == IF_NDEF:
                    new_node = Session(data[1])
                    new_node.cur_state = 2
                    if node.cur_state == 1:
                        node.define_data.append(new_node)
                    else:
                        node.notdefine_data.append(new_node)
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif data[0] == IF_DEF:
                    new_node = Session(data[1])
                    new_node.cur_state = 1
                    if node.cur_state == 1:
                        node.define_data.append(new_node)
                    else:
                        node.notdefine_data.append(new_node)
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif data[0] == ELSE:
                    if node.cur_state == 1:
                        node.cur_state = 2
                    elif node.cur_state == 2:
                        node.cur_state = 1

                index += 1
                if index >= len(context):
                    break
                data = self._split_string(context[index][0])
            index += 1
        self._cpp_data = root

    def _load_and_reomve_notes(self, f):
        """ 读取文件，去除注释和空行，屏蔽掉字符串和字符。

         屏蔽掉的字符串和字符使用特殊符号代替（该特殊符号不会在cpp宏定义除字符串、字符、注释以外出现）
         处理完成之后再重新还原

         :return 返回一个列表，列表中每一项是一个元组（data,[old_string]），data是宏定义，old_string
         列表是被屏蔽掉的字符串或字符
         """

        context = []
        is_notes = False
        try:
            with open(f, 'r') as p:
                line = p.readline()
                while line:
                    is_notes = self._remove_notes(context, line)
                    if is_notes:
                        next_line = p.readline()
                        if next_line:
                            line = line + next_line  # /*注释在当前行未匹配到结束，把下一行拼接到当前行重新操作
                        else:
                            end = line.rfind('/*')  # 文件没有下一行了，无法匹配到*/，直接删除最后的/*后面的内容
                            line = line[:end]
                    else:
                        line = p.readline()
        except:
            raise
        return context

    def _remove_notes(self, context, line):
        """删除注释 """

        if (line.find('//') > -1):
            if line.find('\"') > -1 and line.find('\"') < line.find('//'):
                pass
            elif line.find('/*') > -1 and line.find('/*') < line.find('//'):
                pass
            elif line.find('\'') > -1 and line.find('\'') < line.find('//'):
                pass
            else:
                start = line.find('//')  # 删除最前面“//”注释
                line = line[:start]

        # 屏蔽掉字符串，删除注释后再插入原来的位置
        old_string = []  # 里面的项为(原字符串),在去除掉注释后再插入
        new_line, is_notes = self._mask_string(line, old_string)
        if is_notes:
            return is_notes
        else:
            line = new_line

        start = line.find('//')  # 删除'/**/'注释和字符串后面的“//”注释
        if start > -1:
            line = line[:start]

        start = line.find(';')  # 删除；后面的内容
        if start > -1:
            line = line[:start]

        line = line.strip()  # 去掉两端的空格
        if line != '' or is_notes:
            context.append((line, old_string))
        return is_notes

    def _mask_string(self, line, old_string):
        """ 屏蔽字符串，字符"""

        start = 0
        end = start
        state = 0  # 0表示没有匹配，1：正在匹配“”，2：正在匹配‘’，3：正在匹配/**/ ，4：正在匹配转义符\,
        old_state = 0
        old_char = ''
        for i in line:
            flag = False
            if state == 0:
                if i == '\"':
                    state = 1
                    start = end
                elif i == '\'':
                    state = 2
                    start = end
                elif i == '*':
                    if old_char == '/':
                        state = 3
                        start = end - 1
                        flag = True
                elif i == '\\':
                    state = 4
                elif i == '/':
                    if old_char == '/':
                        line = line[:end - 1]
                        return line, False
            else:
                if i == '\\' and old_char != '\\' and state != 3:
                    old_state = state
                    state = 4
                elif state == 1 and i == '\"' and old_char != '\\':  # 结束匹配
                    line = self._my_replace(line, start, end, old_string, STRING_PLACEHOLDER)
                    state = 0
                    return self._mask_string(line, old_string)
                elif state == 2 and i == '\'' and old_char != '\\':
                    line = self._my_replace(line, start, end, old_string, CHAR_PLACEHOLDER)
                    state = 0
                    return self._mask_string(line, old_string)
                elif state == 3 and i == '/' and old_char == '*':
                    line = self._my_replace(line, start, end, [], ' ')
                    state = 0
                    return self._mask_string(line, old_string)
                elif state == 4:
                    state = old_state
                    flag = True
            old_char = i
            end += 1
            if flag:
                old_char = ''

        if state != 3 and state != 0:
            raise Exception('missing \"or \'')
        if state == 3:
            return line, True
        else:
            return line, False

    def _my_replace(self, line, start, end, save_list, placeholder):
        sub_string = line[start:end + 1]
        save_list.append(sub_string)
        return line[:start] + placeholder + line[end + 1:]

    def _split_string(self, line):
        start = line.find('#')
        if start > -1:
            line = line[start + 1:]  # 去除‘#’防止出现‘#  define’
        else:
            raise Exception('illegal string')
        item = line.split(None, 2)
        if len(item) == 1:
            if item[0] == END_IF or item[0] == ELSE:
                return [item[0]]
            else:
                raise Exception('error define')
        if len(item) == 2:
            if item[0] == DEFINE or item[0] == IF_DEF or item[0] == IF_NDEF:
                return [item[0], item[1], NONE]
            elif item[0] == END_IF or item[0] == ELSE:
                return [item[0]]
            elif item[0] == UNDEF:
                return [item[0], item[1], UNDEF]
            else:
                raise Exception('error define')
        else:
            if item[0] == IF_DEF or item[0] == IF_NDEF:
                return [item[0], item[1]]
            elif item[0] == END_IF or item[0] == ELSE:
                return [item[0]]
            elif item[0] == DEFINE:
                return [item[0], item[1], item[2]]
            elif item[0] == UNDEF:
                return [item[0], item[1], UNDEF]
            else:
                raise Exception('error define')

    def preDefine(self, s):
        self._pre_define_macros = []
        s = self._escape(s)
        s = self._remove_control_chars(s)
        macros = s.split(';')
        for item in macros:
            item = item.strip()
            if item != '':
                self._pre_define_macros.append(item)

    def _remove_control_chars(self, s):
        """去除不可见字符"""
        for i in range(0, 32):
            s = s.replace(chr(i), '')
        return s

    def dumpDict(self):
        """ 返回一个字典，字典中包含从cpp文件中解析出来的可以宏数据 """

        dump_dict = {}
        for i in self._pre_define_macros:
            dump_dict[i] = None

        try:
            self._convert_session_datas(self._cpp_data, dump_dict)
        except:
            raise

        # dump_dict =self._escape_dump_dict(self._dump_dict)
        return dump_dict

    def _convert_session_datas(self, node, dump_dict):
        """ 根据预定义的宏，解析Session数据，将解析出来的数据存储到dump_dict中"""

        if node == None:
            return
        index = dump_dict.keys().count(node.key)
        if index > 0:
            for item in node.define_data:
                if isinstance(item, Session):
                    self._convert_session_datas(item, dump_dict)
                else:
                    k, (v, real_str) = item
                    if v == 'undef':
                        del dump_dict[k]
                    else:
                        dump_dict[k] = self._convert_cpp_to_python((v, real_str))

        else:
            for item in node.notdefine_data:
                if isinstance(item, Session):
                    self._convert_session_datas(item, dump_dict)
                else:
                    k, (v, real_str) = item
                    if v == 'undef':
                        del dump_dict[k]
                    else:
                        dump_dict[k] = self._convert_cpp_to_python((v, real_str))

    def _convert_tuple(self, tup_str):
        """ 将聚合字符串转换为元组"""
        s, real_str = tup_str
        stack = []
        head = TupleData()
        stack.append(head)
        index = 0
        start = 0
        # end = start
        while len(stack) > 0 and index < len(s):
            node = stack.pop()
            while index < len(s):
                i = s[index]
                index += 1
                if i == ',':
                    data = s[start:index - 1]
                    if data.strip() != '':
                        node.data.append(self._convert_rest(data, real_str))
                    start = index
                elif i == '{':
                    new_node = TupleData()
                    node.data.append(new_node)
                    start = index
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif i == '}':
                    data = s[start:index - 1]
                    node.data.append(self._convert_rest(data, real_str))
                    start = index
                    node = stack.pop()

        return self._resolve_tuple_data(head.data.pop(0))

    def _resolve_tuple_data(self, node):
        dict_item = ()
        for i in node.data:
            if isinstance(i, TupleData):
                sub = self._resolve_tuple_data(i)
                # if len(sub)>0:
                dict_item = dict_item + (sub,)
            else:
                if i != None:
                    dict_item = dict_item + (i,)

        return dict_item

    def _convert_cpp_to_python(self, s):
        """ 转换cpp数据为python数据 """
        try:
            v, real_str = s
            temp_v = []
            for i in real_str:
                temp_v.append(i)
            if v.find('{') > -1:
                return self._convert_tuple((v, temp_v))

            return self._convert_rest(v, temp_v)
        except:
            raise

    def _convert_rest(self, v, real_str):
        """ 转换非聚合部分"""
        if v.strip() == '':
            return None
        if v == 'false':
            return False
        if v == 'true':
            return True
        if v == NONE:
            return None

        # 处理字符常量
        if v.find(CHAR_PLACEHOLDER) > -1:
            # 把保存的字符常量还原
            while v.find(CHAR_PLACEHOLDER) > -1:
                replace_index = v.find(CHAR_PLACEHOLDER)
                if len(real_str) == 0:
                    raise ValueError
                v = v[:replace_index] + real_str.pop(0) + v[replace_index + 2:]

            v, need_minus_sign = self._sign_strip(v)
            if need_minus_sign:
                return -self._cppchar_to_integer(v[1:-1])
            else:
                return self._cppchar_to_integer(v[1:-1])

        # 处理字符串
        if v.find(STRING_PLACEHOLDER) > -1:
            # 去掉##或者空格（使用##或空格拼接拼接的字符串）
            v = v.replace('##', '')
            v = v.replace(' ', '')

            is_W_string = False
            if v.find('L' + STRING_PLACEHOLDER) > -1:
                is_W_string = True
            v = v.replace('L', '')

            # 把保存的字符串还原
            while v.find(STRING_PLACEHOLDER) > -1:
                replace_index = v.find(STRING_PLACEHOLDER)
                string_temp = real_str.pop(0)
                string_temp2 = string_temp[1:-1]
                v = v[0:replace_index] + string_temp2 + v[replace_index + 2:]

            if is_W_string:  # 转换宽字符串
                return self._escape(v.decode('utf-8'))  # encode('string_escape')
            else:  # 转换字符串
                return self._escape(v)


        # 去除符号前缀，并计算正负号
        v, need_minus_sign = self._sign_strip(v)


        # 转换为整数
        try:
            integer = self._to_python_integer(v)
            if need_minus_sign:
                return -integer
            else:
                return integer
        except:
            try:
                float_num = self._to_python_float(v)
                if need_minus_sign:
                    return -float_num
                else:
                    return float_num
            except:
                raise Exception(v+' convert float fail!')

        raise ValueError

    def _remove_integer_suffix(self, v):
        suffix = ['UI64','I64','ULL','UL', 'U', 'L' ]
        v = v.upper()
        for i in suffix:
            if v.endswith(i):
                v = v[:-len(i)]
                break
        return v

    def _remove_float_suffix(self, v):
        v = v.upper()
        if v.endswith('L') or v.endswith('F'):
            v=v[:-1]
        return v

    def _sign_strip(self, s):
        """ 去除符号前缀，返回是否是负数 """
        mid = 0
        for i in s:
            if i == ' ' or i == '+' or i == '-':
                mid += 1
            else:
                break
        symbol = s[:mid]
        data = s[mid:]
        symbol = symbol.replace('+', '')
        count = symbol.count('-') % 2
        if count == 0:
            return data.strip(), False
        else:
            return data.strip(), True

    def _to_python_float(self, v):
        # 去除后缀
        v = self._remove_float_suffix(v)
        return float(v)

    def _to_python_integer(self, v):
        # 去除后缀
        v = self._remove_integer_suffix(v)

        if v[:2] == '0X':
            v = v[2:]
            return int(v, 16)
        if v[:1] == '0':
            num = int(v)
            if num > 7:
                return int(v, 8)
            else:
                return num
        if v[:2] == '0B':
            v = v[2:]
            return int(v, 2)
        return int(v)

    def _cppchar_to_integer(self, s):
        res = 0
        new_s = self._escape(s)
        index = len(new_s) - 1
        if index > 3:  # 长度超过4位则取最后四位
            new_s = new_s[-4:]
            index = 3
        for c in new_s:
            res += ord(c) * (256 ** index)
            index -= 1
        return res

    def _escape(self, v):
        """转义"""

        v = self._escape_characters(v)
        v = self._escape_hex_character(v)
        v = self._escape_octal_character(v)
        return v

    def _escape_characters(self, v):
        """ 转义字符 """

        res = []
        cur = 0
        next = 1
        while next < len(v):
            ch = v[cur:next + 1]
            if ch in ESCAPE_MAP.keys():
                res.append(ESCAPE_MAP[ch])
                next += 2
                cur += 2
            else:
                if v[cur]=='\\' and v[next]!='x' and (ord(v[next])<ord('0') or ord(v[next])>ord('7')):
                   pass #滤除无效的转义符‘\’
                else:
                    res.append(v[cur])
                next += 1
                cur += 1
        if cur < len(v):
            res.append(v[cur])
        return ''.join(res)

    def _escape_hex_character(self, s):
        """ 转义十六进制表示法的 ASCII 字符（忽略起始0，然后取两位）"""

        start = 0
        while s.find('\\x', start, len(s)) > -1:
            start = s.find('\\x', start, len(s))
            for i in range(start + 2, len(s)):
                character = s[i]
                if (ord('0') <= ord(s[i]) <= ord('9') or ord('a') <= ord(s[i]) <= ord('f') or
                    ord('A') <= ord(s[i]) <= ord('F')
                ) and int(s[start + 2:i + 1], 16) < 256:
                    continue
                else:
                    i -= 1
                    break
            if i > start:
                try:
                    escape_str = s[start + 2:i + 1]
                    num = int(escape_str, 16)
                except:
                    raise Exception('illegal num ')
                after_escape = chr(num)
                s = s[:start] + after_escape + s[i + 1:]
        return s

    def _escape_octal_character(self, s):
        """ 转义八进制表示法的 ASCII 字符（最多取3位）"""

        index=0
        start = 0
        while index<len(s):
            if s[index]!='\\':
                index+=1
                continue
            start =index
            for i in range(start + 1, start + 5):
                if i < len(s) and ord('0') <= ord(s[i]) < ord('8') and int(s[start + 1:i + 1], 8) < 256:
                    continue
                else:
                    i -= 1
                    break
            if i > start + 1:
                # escape_str=s[start:i]
                num = int(s[start + 1:i + 1], 8)
                after_escape = chr(num)
                s = s[:start] + after_escape + s[i + 1:]
            else:
                index+=1
        return s

    def dump(self, f):
        """ 将数据重新存储为.cpp宏文件 """

        dump_dict = self.dumpDict()
        try:
            with open(f, 'w') as p:
                for k, v in dump_dict.items():

                    if self._is_w_string(v):
                        v = 'L\"' + self._revoke_escape(v) + '\"'
                    elif self._is_string(v):
                        v = '\"' + self._revoke_escape(v) + '\"'
                    elif v is False:
                        v = 'false'
                    elif v is True:
                        v = 'true'
                    elif v is None:
                        v = ''
                    elif self._is_tuple(v):
                        v = self._tuple_to_string(v)
                        v = v.replace(',}', '}')
                    p.write('#define ' + str(k) + ' ' + str(v) + '\n')
        except:
            raise

    def _tuple_to_string(self, s):
        """ 将python中的元组转换回cpp中的聚合字符串 """

        res = []
        res.append('{')
        for v in s:
            if isinstance(v, tuple):
                res.append(self._tuple_to_string(v))
            elif self._is_w_string(v):
                res.append('L\"' + self._revoke_escape(v) + '\"')
            elif self._is_string(v):
                res.append("\"" + self._revoke_escape(v) + '\"')
            elif v is False:
                res.append('false')
            elif v is True:
                res.append('true')
            elif v is None:
                res.append('')
            else:
                res.append(str(v))
            res.append(',')
        res.append('}')
        return ''.join(res)

    def _revoke_escape(self, s):
        """ 将转义字符转换成可写入文件中的形式 """

        res = []
        for ch in s:
            if ch in REVOKE_ESCAPE_MAP.keys():
                res.append(REVOKE_ESCAPE_MAP[ch])
            else:
                res.append(ch)
        return ''.join(res)

    def _is_tuple(self, obj):
        try:
            return isinstance(obj, tuple)
        except:
            return False

    def _is_w_string(self, obj):
        try:
            return isinstance(obj, unicode)
        except:
            return False
        else:
            return True

    def _is_string(self, obj):
        try:
            obj + ''
        except:
            return False
        else:
            return True


if __name__ == "__main__":
    a1 = PyMacroParser()
    a1.load('a.cpp')
    a1.dump('b.cpp')
    print a1.dumpDict()
    a1.load('b.cpp')
    a1.dump('c.cpp')
    a1.preDefine(';')
    print a1.dumpDict()
    a1.dump('d.cpp')

    # a1.preDefine('MC1;MC2;MC3;MC4')  # 指定预定义宏，再dump
    # print  a1.dumpDict()
    # a1.dump('c.cpp')
    #
    # a1.preDefine('   \f\n\r\tMC1; \t\\MC2; \v\vMC3\t; \fMC4')
    # print a1.dumpDict()
