#! coding:utf-8

import string

class Session(object):
    def __init__(self, s):
        self.key = s
        #self.define_list = []
        #self.notdefine_list = []
        self.define_data = []
        self.notdefine_data = []
        self.cur_state = 2

class TupleData(object) :
     def __init__(self) :
        self.data = []
        # self.child_tuple_data = []
        # self.right_data=None


def split_string(line):
    start=line.find('#')
    if start>-1:
         line=line[start+1:] #去除‘#’防止出现‘#  define’
    else:
        raise Exception('illegal string')
    item=line.split(None,2)
    if len(item)==1:
        if item[0]=='endif' or item[0]=='else':
            return [item[0]]
        else:
            raise Exception('error define')
    if len(item)==2:
        if item[0]=='define' or item[0]=='ifdef' or item[0]=='ifndef':
            return [item[0],item[1],'None']
        elif item[0]=='endif' or item[0]=='else':
            return [item[0]]
        elif item[0]=='undef':
            return [item[0], item[1], 'undef']
        else:
            raise Exception('error define')
    else:
        if item[0]=='ifdef' or item[0]=='ifndef':
            return [item[0],item[1]]
        elif item[0]=='endif' or item[0]=='else':
            return [item[0]]
        elif item[0]=='define':
            return [item[0],item[1],item[2]]
        elif item[0]=='undef':
            return [item[0], item[1], 'undef']
        else:
            raise Exception('error define')


string_placeholder='%%'
char_placeholder='@@'

class PyMacroParser(object):
    """
      Resolve all available macro definitions in Cpp files
    """
    def __init__(self):
        self._pre_define_macros=[]
        self._read_define_macros=[]
        self._root=None
        #self._dump_dict={}

    def _str_to_tuple(self, tup_str):
        s,real_str=tup_str
        stack = []
        head = TupleData()
        stack.append(head)
        index = 0
        start = 0
        # end = start
        while len(stack) > 0 and index < len(s):
            node = stack.pop()
            while index<len(s):
                i=s[index]
                index+=1
                if i == ',':
                    data=s[start:index-1]
                    if data.strip()!='':
                        node.data.append(self._convert_rest(data,real_str))
                    start=index
                elif i=='{':
                    new_node=TupleData()
                    node.data.append(new_node)
                    start=index
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif i=='}':
                    data = s[start:index - 1]
                    node.data.append(self._convert_rest(data, real_str))
                    start = index
                    node = stack.pop()


        return self._resolve_tuple_data(head.data.pop(0))

    def _resolve_tuple_data(self,node):
        dict_item=()
        for i in node.data:
            if isinstance(i,TupleData):
                sub=self._resolve_tuple_data(i)
                #if len(sub)>0:
                dict_item=dict_item+(sub,)
            else:
                if i!=None:
                    dict_item=dict_item+(i,)

        return dict_item

    def _convert_cpp_to_python (self, s):
        try:
            # 转换聚合数据为元组
            v, real_str = s
            temp_v=[]
            for i in real_str:
                temp_v.append(i)
            if v.find('{')>-1:
                return self._str_to_tuple((v, temp_v))

            return self._convert_rest(v,temp_v)
        except :
            raise


    def _convert_rest(self, v,real_str):
        tempv=v
        if v.strip()=='':
            return None
        if v=='false':
            return False
        if v=='true':
            return True
        if v=='None':
            return None

        # 处理字符常量
        if v.find(char_placeholder) > -1:
            # 把保存的字符常量还原
            while v.find(char_placeholder) > -1:
                replace_index = v.find(char_placeholder)
                if len(real_str)==0:
                    raise ValueError
                v = v[:replace_index] + real_str.pop(0) + v[replace_index + 2:]

            v, need_minus_sign = self._sign_strip(v)
            if need_minus_sign:
                 return -self._chartointeger(v[1:-1])
            else:
                return self._chartointeger(v[1:-1])

        #处理字符串
        if v.find(string_placeholder) > -1:
            # 去掉##或者空格（使用##或空格拼接拼接的字符串）
            v=v.replace('##','')
            v=v.replace(' ','')

            is_W_string=False
            if v.find("L"+string_placeholder)>-1:
                is_W_string=True
            v=v.replace("L",'')

            # 把保存的字符串还原
            while v.find(string_placeholder) > -1:
                replace_index = v.find(string_placeholder)
                string_temp=real_str.pop(0)
                string_temp2=string_temp[1:-1]
                v = v[0:replace_index] +string_temp2 + v[replace_index + 2:]


            if is_W_string:#转换宽字符串
                return self._escape_characters(v.decode('utf-8')) #encode('string_escape')
            else: #转换字符串
                return self._escape_characters(v)

        #计算正负号
        v,need_minus_sign=self._sign_strip(v)

        # 转换为整数
        try:
            integer = self._str_to_num(v)
            if need_minus_sign:
                return  -integer
            else:
                 return integer
        except:
            try:
                float_num=self._to_float(v)
                if need_minus_sign:
                    return -float_num
                else:
                    return float_num
            except:
               raise Exception('convert float fail!')

        raise ValueError


    def _to_float(self,v):
        # 转换有f的浮点型
        if  v.find('f') > -1:
            return string.atof(v.replace('f', ''))

        # 转换有F的浮点型
        if  v.find('F') > -1:
            return string.atof(v.replace('F', ''))

        # 转换有l的浮点型
        if v.find('l') > -1:
            return string.atof(v.replace('l', ''))

        # 转换有L的浮点型
        if v.find('L') > -1:
            return string.atof(v.replace('L', ''))

        # 转换没有f的浮点型
        return float(v)

    def _str_to_num(self,v):
        v=v.replace('u','')
        v=v.replace('U','')
        v=v.replace('l','')
        v=v.replace('L','')

        if v[:2]=='0x' or v[:2]=='0X':
            v=v[2:]
            return int(v,16)
        if v[:1]=='0':
            num=int(v)
            if num>7:
                return int(v,8)
            else:
                return num
        if v[:2]=='0b' or v[:2]=='0B':
            v=v[2:]
            return int(v,2)
        return int(v)

    def _chartointeger(self, s):
        res=0

        # new_s=s[-4:]
        # index=len(new_s)
        # for c in s[-4:]:
        #     res += ord(c) * (256 ** index)
        #     index -= 1
        # return res


        new_s=self._escape_characters(s)
        # s=self._escape_hex_character(s)
        # s=self._escape_octal_character(s)
        index=len(new_s)-1
        if index>3:
            #raise Exception('Too many characters in character constants')
            new_s=new_s[-4:]
            index=3
        for c in new_s:
            res+=ord(c)*(256**index)
            index-=1
        return  res

    def _escape_hex_character(self,s):
        #忽略起始0，然后取两位
        start = 0
        while s.find('\\x', start, len(s)) > -1:
            start = s.find('\\x', start, len(s))
            for i in range(start + 2, len(s)):
                character = s[i]
                if (ord('0') <= ord(s[i]) <= ord('9') or ord('a')<=ord(s[i])<=ord('f') or
                 ord('A')<=ord(s[i])<=ord('F')
                )and int(s[start + 2:i + 1], 16) < 256:
                    continue
                else:
                    i-=1
                    break
            if i > start:
                try:
                    escape_str=s[start+2:i+1]
                    num = int(escape_str, 16)
                except:
                    raise Exception('illegal num ')
                after_escape = chr(num)
                s = s[:start] + after_escape + s[i+1:]
        return s

    def _escape_octal_character(self,s):
        #最多取3位
        start=0
        while s.find('\\',start,len(s))>-1:
            start=s.find('\\',start,len(s))
            for i in range(start+1,start+5):
                if i<len(s) and ord('0')<=ord(s[i])<ord('8') and int(s[start+1:i+1],8)<256:
                    continue
                else:
                    i-=1
                    break
            if i>start+1:
                # escape_str=s[start:i]
                num=int(s[start+1:i+1],8)
                after_escape=chr(num)
                s=s[:start]+after_escape+s[i+1:]
            else:
                s=s[:start]+s[start+1:]
        return s

    def _sign_strip(self,s):
        mid=0
        for i in s:
            if i==' ' or i=='+' or i=='-':
                mid+=1
            else:
                break
        symbol=s[:mid]
        data=s[mid:]
        symbol=symbol.replace('+','')
        count=symbol.count('-')%2
        if count==0:
            return data.strip(),False
        else:
            return data.strip(),True

    def _escape_tuple(self,v):
        res=()
        for i in v:
            if isinstance(i,tuple):
                res=res+(self._escape_tuple(i),)
            else:
                res=res+(self._escape_characters(i),)
        return res

    def _escape_characters(self,v):
        if self._is_string(v) or self._is_w_string(v):
            if v.find('\\\\')>-1:
                v=v.replace('\\\\',string_placeholder)
            # if v.find('\\?')>-1:
            #     v= v.replace('\\f','?')
            if v.find('\\f')>-1:
                v= v.replace('\\f','\x0c')
            if v.find('\\n')>-1:
                v=v.replace('\\n','\n')
            if v.find('\\t')>-1:
                v=v.replace('\\t','\t')
            if v.find('\\r') > -1:
                v = v.replace('\\r', '\r')
            if v.find('\\\'')>-1:
                v=v.replace('\\\'',"'")
            if v.find('\\\"')>-1:
                v = v.replace('\\\"', '"')
            if v.find('\\a')>-1:
                v = v.replace('\\a', '\x07')
            if v.find('\\b')>-1:
                v = v.replace('\\b', '\x08')
            if v.find('\\v')>-1:
                v = v.replace('\\v', '\x0b')

            v = self._escape_hex_character(v)
            v = self._escape_octal_character(v)

            v=v.replace(string_placeholder,'\\')
        return v

    def _convert_session_datas(self, node, dump_dict):
        if node==None:
            return
        index = dump_dict.keys().count(node.key)
        if index > 0:
            for item in node.define_data:
                if isinstance(item,Session):
                    self._convert_session_datas(item, dump_dict)
                else:
                    k, (v, real_str)=item
                    if v=='undef':
                        del dump_dict[k]
                    else :
                        dump_dict[k]=self._convert_cpp_to_python((v, real_str))

        else:
            for item in node.notdefine_data:
                if isinstance(item,Session):
                    self._convert_session_datas(item, dump_dict)
                else:
                    k, (v, real_str) = item
                    if v == 'undef':
                        del dump_dict[k]
                    else:
                        dump_dict[k] = self._convert_cpp_to_python((v, real_str))

    def _load_and_reomve_notes(self,f):
        context=[]
        is_notes=False
        try:
            with open(f, 'r') as p:
                line=p.readline()
                while line:
                    is_notes=self.remove_notes(context,line)
                    if is_notes:
                        next_line=p.readline()
                        if next_line:
                            line=line+next_line#/*注释在当前行未匹配到结束，把下一行拼接到当前行重新操作
                        else:
                            end=line.rfind('/*') #文件没有下一行了，无法匹配到*/，直接删除最后的/*后面的内容
                            line=line[:end]
                    else:
                        line=p.readline()
        except :
             raise
        return context

    def _my_replace(self,line,start,end,save_list,placeholder):
        sub_string=line[start:end+1]
        save_list.append(sub_string)
        return  line[:start]+placeholder+line[end+1:]

    def _replace_string(self,line,old_string):
        start=0
        end = start
        state=0   #0表示没有匹配，1：正在匹配“”，2：正在匹配‘’，3：正在匹配/**/ ，4：正在匹配转义符\,
        old_state=0
        old_char=''
        for i in line:
            flag=False
            if state==0:
                if i=='\"':
                    state=1
                    start=end
                elif i=='\'':
                    state=2
                    start=end
                elif i=='*':
                     if old_char=='/':
                        state=3
                        start=end-1
                        flag=True
                elif i=='\\':
                    state=4
                elif i=='/':
                    if old_char=='/':
                        line=line[:end-1]
                        return line,False
            else:
                if i == '\\' and old_char!='\\' and state!=3:
                    old_state = state
                    state = 4
                elif state==1 and i=='\"' and old_char!='\\':#结束匹配
                    line = self._my_replace(line, start, end,  old_string,string_placeholder)
                    state=0
                    return self._replace_string(line, old_string)
                elif state==2 and i=='\''and old_char!='\\':
                    line = self._my_replace(line,start,end,old_string,char_placeholder)
                    state=0
                    return self._replace_string(line, old_string)
                elif state==3 and i=='/'and old_char=='*':
                    line = self._my_replace(line, start, end, [], ' ')
                    state=0
                    return self._replace_string(line, old_string)
                elif state==4:
                    state=old_state
                    flag=True
            old_char = i
            end+=1
            if flag:
                old_char=''

        if state!=3 and state!=0:
            raise Exception('missing \"or \'')
        if state==3:
            return line,True
        else:
            return line,False

    def remove_notes(self, context, line):

        if (line.find("//") > -1 ):
             if line.find('\"')>-1 and line.find('\"')<line.find('//'):
                pass
             elif line.find('/*')>-1 and line.find('/*')<line.find('//'):
                 pass
             elif line.find('\'')>-1 and line.find('\'')<line.find('//'):
                 pass
             else:
                start = line.find("//")  # 删除最前面“//”注释
                line = line[:start]

        # 屏蔽掉字符串，删除注释后再插入原来的位置
        old_string = []  # 里面的项为(原字符串),在去除掉注释后再插入
        new_line,is_notes=self._replace_string(line,old_string)
        if is_notes:
            return is_notes
        else:
            line=new_line
        # if is_notes:
        #     start=line.find("/*")
        #     if start>-1:
        #         line=line[:start]
        start = line.find("//")  # 删除"/**/"注释和字符串后面的“//”注释
        if start > -1:
            line = line[:start]

        start = line.find(";")  # 删除；后面的内容
        if start > -1:
            line = line[:start]

        line = line.strip()  # 去掉两端的空格
        if line != "" or is_notes:
            # for s in old_string:
            #     start=line.find(':')
            #     line = line[:start]+s+line[start+1:]
            context.append((line,old_string))
        return is_notes

    def load(self,f):
        """
        Load Cpp file

        :param f:cpp file path
        :return: None
        """
        #self._pre_define_macros = []
        self._root = None
        self._dump_dict = {}

        try:
            context=self._load_and_reomve_notes(f)
        except:
            raise
        root=Session('root')
        stack=[]
        stack.append(root)
        index=0
        while len(stack)>0 and index<len(context):
            node=stack.pop()
            data=split_string(context[index][0])
            while data[0]!='endif' and index<len(context):
                if data[0]=='define' or data[0]=='undef':
                    # if data[2]=='None':
                    #     data[2]=data[1] #第三项为“”None则直接使用第1，0项作为key，value(key不能相同，所以用第二项作为key)
                    #     data[1]=data[0]
                    if node.cur_state==1:
                        node.define_data.append((data[1],(data[2],context[index][1])))
                    else:
                        node.notdefine_data.append((data[1],(data[2],context[index][1])))
                elif data[0]=='ifndef':
                    new_node=Session(data[1])
                    new_node.cur_state=2
                    if node.cur_state==1:
                        node.define_data.append(new_node)
                    else:
                        node.notdefine_data.append(new_node)
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif data[0]=='ifdef':
                    new_node=Session(data[1])
                    new_node.cur_state=1
                    if node.cur_state==1:
                        node.define_data.append(new_node)
                    else:
                        node.notdefine_data.append(new_node)
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif data[0]=='else':
                    if node.cur_state==1:
                        node.cur_state=2
                    elif node.cur_state==2:
                        node.cur_state=1

                index += 1
                if index >= len(context):
                    break
                data = split_string(context[index][0])
            index += 1

        self._root=root
        # try:
        #     self._dump_dict={}
        #     self._convert_session_datas(self._root, self._pre_define_macros, self._dump_dict)
        # except:
        #     raise

    def preDefine(self,s):
        """
        Macros predefined

        :param s:Pre-defined macro string,split with ";" of macros
        :return:None
        """
        self._pre_define_macros=[]
        s=self._escape_characters(s)
        s=self._remove_control_chars(s)
        macros=s.split(';')
        for item in macros:
            item=item.strip()
            if item!='':
                self._pre_define_macros.append(item)

    def _remove_control_chars(self,s):
        for i in range(0, 32):
            s = s.replace(chr(i), '')

        return s

    def dumpDict(self):
        """
        Resolve all available macro to a dict

        :return:dict
        """

        dump_dict={}
        for i in self._pre_define_macros:
            dump_dict[i] = None

        try:
            self._convert_session_datas(self._root, dump_dict)
        except:
            raise

        # dump_dict =self._escape_dump_dict(self._dump_dict)
        return dump_dict


    def dump(self,f):
        """
        Output all available macros stored in the new Cpp file

        :param f:file path
        :return:None
        """

        dump_dict=self.dumpDict()
        try:
            with open(f, 'w') as p:
                for k,v in dump_dict.items():

                    if self._is_w_string(v):
                        v =  "L\"" + self._revoke_escape(v) + "\""
                    elif self._is_string(v):
                        v="\""+self._revoke_escape(v)+"\""
                    elif v is False:
                        v='false'
                    elif v is True:
                        v='true'
                    elif v is None:
                        v=''
                    elif self._is_tuple(v):
                        v=self._tuple_to_string(v)
                        v=v.replace(',}','}')
                    p.write('#define '+str(k)+' '+ str(v)+'\n')
        except :
             raise
    def _tuple_to_string(self,s):
        res=''
        res+='{'
        for v in s:
            if isinstance(v,tuple):
                res+=self._tuple_to_string(v)
            elif self._is_w_string(v):
                res+= "L\"" + self._revoke_escape(v) + "\""
            elif self._is_string(v):
                res+= "\"" + self._revoke_escape(v) + "\""
            elif v is False:
                res+= 'false'
            elif v is True:
                 res+= 'true'
            elif v is None:
                  res+= ''
            else:
                res+=str(v)
            res+=','
        res+='}'
        return res
    def _revoke_escape(self,s):
        res=''
        for ch in s:
            if ch=='\\':
                res+='\\\\'
            elif ch=='\f':
                res+='\\f'
            elif ch=='\n':
                res+='\\n'
            elif ch=='\t':
                res+='\\t'
            elif ch == '\r':
                res += '\\r'
            elif ch == '\a':
                res += '\\a'
            elif ch == '\b':
                res += '\\b'
            elif ch == '\v':
                res += '\\v'
            elif ch == '\'':
                res += '\\\''
            elif ch == '\"':
                res += '\\\"'
            else:
                res+=ch
        return res


    def _is_tuple(self,obj):
        try:
            return isinstance(obj,tuple)
        except:
            return False

    def _is_w_string(self,obj):
        try:
           return isinstance(obj,unicode)
        except:
            return False
        else:
            return True

    def _is_string(self,obj):
        try:
            obj+''
        except:
            return False
        else:
            return True

if __name__ == "__main__":

    a1 = PyMacroParser()
    a1.load("a.cpp")
    a1.dump("b.cpp")
    print a1.dumpDict()
    a1.load("b.cpp")
    a1.dump("c.cpp")
    a1.preDefine(";")
    print a1.dumpDict()
    a1.dump("d.cpp")

    # a1 = PyMacroParser()
    # a1.load("a3.cpp")
    # a1.preDefine("MC1;MC2")
    # print a1.dumpDict()
    # a1.dump('b.cpp')
    # print '---------'
    #
    # a2 = PyMacroParser()
    # a2.preDefine("MC1;MC2")
    # print a2.dumpDict()
    # a2.dump('c.cpp')
    # a2.dump('d.cpp')

    # a1.preDefine("MC1;MC2;MC3;MC4")  # 指定预定义宏，再dump
    # print  a1.dumpDict()
    # a1.dump("c.cpp")
    #
    # a1.preDefine("   \f\n\r\tMC1; \t\\MC2; \v\vMC3\t; \fMC4")
    # print a1.dumpDict()

    






