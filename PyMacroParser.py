#! coding:utf-8

import string

class Session(object):
    def __init__(self, s):
        self.key = s
        self.define_list = []
        self.notdefine_list = []
        self.define_data = []
        self.notdefine_data = []
        self.cur_state = 2

class TupleData(object) :
     def __init__(self) :
        self.data = []
        self.child_tuple_data = []

def split_string(line):
    start=line.find('#')
    if start>-1:
         line=line[start+1:] #去除‘#’防止出现‘#  define’
    else:
        raise Exception('illegal string')
    item=line.split()
    if len(item)==1:
        return [item[0]]
    if len(item)==2:
        return [item[0],item[1],'None']
    else:
        start=line.find(item[1])
        before_three=line[:start+len(item[1])]
        three=line.replace(before_three,"").strip()
        return [item[0],item[1],three]



class PyMacroParser(object):
    """
      Resolve all available macro definitions in Cpp files
    """
    def __init__(self):
        self._pre_define_macros=[]
        self._dump_dict={}

    def _strtotuple(self,tup_str):
        s,real_str=tup_str
        stack = []
        root = TupleData()
        stack.append(root)
        index = 0
        start = 0
        # end = start
        while len(stack) > 0 and index < len(s):
            node = stack.pop()
            while index<len(s):
                i=s[index]
                index+=1
                if i == ','or index==len(s):
                    if index==len(s):
                        data = s[start:]
                    else:
                       data=s[start:index-1]
                    node_finished=False
                    if data.find('}')>-1:
                        data=data.replace('}','')
                        node_finished=True
                    while data.find('$')>-1:
                        replace_index=data.find('$')
                        data=data[:replace_index]+real_str.pop(0)+data[replace_index+1:]
                    node.data.append(self._convert_rest(data))
                    start=index
                    if node_finished==True:
                        break;
                elif i=='{':
                    new_node=TupleData()
                    node.child_tuple_data.append(new_node)
                    start=index
                    stack.append(node)
                    stack.append(new_node)
                    break
        return self._resolve_tuple_data(root)

    def _resolve_tuple_data(self,node):
        dict_item=()
        for i in node.data:
            dict_item=dict_item+(i,)
        for item in node.child_tuple_data:
            dict_item=dict_item+(self._resolve_tuple_data(item),)
        return dict_item

    def _convert_cpp_to_python (self, s):
        try:
            # 转换聚合数据为元组
            v, real_str = s
            if v.find('{')>-1:
                start=v.find('{')
                end=v.rfind('}')
                if end==-1 or end<start:
                    raise Exception('missing }')
                return self._strtotuple((v[start+1:end],real_str))

            #把保存的字符串还原
            while v.find('$') > -1:
                replace_index = v.find('$')
                v = v[:replace_index] + real_str.pop(0) + v[replace_index + 1:]
            return self._convert_rest(v)
        except :
            raise Exception('resolve error')


    def _convert_rest(self, v):
        v=v.strip()
        if v=='':
            return v
        if v=='false':
            return False
        if v=='true':
            return True
        if v=='None':
            return None
        index = v.find("L\"")
        if index > -1:
            v = v.replace('L\"', "")
            v = v.replace('\"', "")
            return v.decode('utf-8')

        index = v.find("\"")
        if index > -1:
            return v.replace("\"", "")

        # 转换字符常量
        if v[0] == '\'' and v[-1] == '\'':
            return self._chartointeger(v[1:-1])

        #转换有f的浮点型
        if v.find("\"")==-1 and v.find('{')==-1 and v.find('f')>-1:
            return string.atof(self._sign_strip(v.replace('f','')))

        # 转换有F的浮点型
        if v.find("\"") == -1 and v.find('{') == -1 and v.find('F') > -1:
            return string.atof(self._sign_strip(v.replace('F', '')))

        #其他进制转换为10进制
        v=self._str_to_num(v)

        # 转换为整数
        try:
            integer = string.atoi(self._sign_strip(v))
        except:
            pass
        else:
            return integer

        # 转换没有f的浮点型
        try:
            f =float(self._sign_strip(v))
        except:
            pass
        else:
            return f

        return  v
    def _str_to_num(self,v):
        if v.find('0x')>-1:
            return int(v,16)
        if v.find('0o')>-1:
            return int(v,8)
        if v.find('0b')>-1:
            return int(v,2)
        return v


    def _chartointeger(self, s):
        res=0
        index=len(s)-1
        for c in s:
            res+=ord(c)*(256**index)
            index-=1
        return  res

    def _sign_strip(self,s):
        s=s.replace('+','')
        data=s.split('-')
        count=s.count('-')%2
        if count==0:
            return data[-1].strip()
        else:
            return '-'+data[-1].strip()

    def _convert_session_datas(self, node, defindString):
        index = defindString.count(node.key)
        if index > 0:
            for k,(v,real_str) in node.define_data:
                if k == 'define':
                    if defindString.count(v) == 0:
                        defindString.append(v)
                        self._dump_dict[v]='None'
                elif k == 'undef':
                    if defindString.count(v) > 0:
                        defindString.remove(v)
                        del self._dump_dict[v]
                else :
                    self._dump_dict[k]=self._convert_cpp_to_python((v, real_str))
            for item in node.define_list:
                self._convert_session_datas(item, defindString)
        else:
            for k,(v,real_str) in node.notdefine_data:
                if k == 'define':
                    if defindString.count(v) == 0:
                        defindString.append(v)
                        self._dump_dict[v]='None'
                elif k == 'undef':
                    if defindString.count(v) > 0:
                        defindString.remove(v)
                        del self._dump_dict[v]
                else :
                    self._dump_dict[k]=self._convert_cpp_to_python((v, real_str))
            for item in node.notdefine_list:
                self._convert_session_datas(item, defindString)


    def _load_and_reomve_notes(self,f):
        context=[]
        is_notes=False
        try:
            with open(f, 'r') as p:
                line=p.readline()
                while line:
                    if is_notes==True:  #判断‘*/’结束符是否在当前行
                        end=line.find('*/')
                        if end>-1:
                            line=line.replace(line[0:end+2],"")
                            is_notes=False
                        else:  #当前行还是注释行，跳过
                            line = p.readline()
                            continue
                    is_notes=self.remove_notes(context,line)
                    line=p.readline()
        except :
             raise
        return context

    def remove_notes(self, context, line):

        is_notes=False
        if (line.find("//") > -1 ):
             if line.find('\"')>-1 and line.find('\"')<line.find('//'):
                pass
             elif line.find('/*')>-1 and line.find('/*')<line.find('//'):
                 pass
             else:
                start = line.find("//")  # 删除最前面“//”注释
                line = line[:start]

        # 屏蔽掉字符串，删除注释后再插入原来的位置（TODO?并且把转义字符转成相应的字符）
        old_string = []  # 里面的项为(原字符串),在去除掉注释后再插入
        while line.find('\"') > -1 or line.find('/*') > -1:  # 找到"字符串则存储，并删掉，找到注释/*直接删掉
            str_start = line.find('\"')
            notes_start = line.find('/*')
            if str_start > -1 and notes_start > -1:  # 两个同时找到，则看那个在前面
                if str_start < notes_start:  # 字符串在前面
                    end = str_start
                    is_escape = False
                    for i in line[str_start + 1:]:
                        end += 1
                        if is_escape:
                            is_escape = False
                            if i=='\"':
                               continue
                        if i == '\\':
                            is_escape = True
                        if i == '\"':
                            break
                    old_string.append(line[str_start:end + 1])
                    line = line.replace(line[str_start:end + 1], '$')
                    continue
                else:  # 注释/*在前面
                    if line.find('*/', notes_start+2, len(line)) > -1:
                        sub_string=line[notes_start:line.find('*/',notes_start+2,len(line)) + 2]
                        line = line.replace(sub_string, '')
                        continue
                    else:  # */在下一行,删除/*后面的东西
                        line = line[:notes_start]
                        is_notes = True
                        break
            elif str_start > -1:  # 没有/*注释
                end = str_start
                is_escape = False
                for i in line[str_start + 1:]:
                    end += 1
                    if is_escape:
                        is_escape = False
                        if i == '\"':
                            continue
                    if i == '\\':
                        is_escape = True
                    if i == '\"':
                        break
                old_string.append(line[str_start:end + 1])
                line = line.replace(line[str_start:end + 1], '$')
                continue
            elif notes_start>-1:#没有字符串
                if line.find('*/', notes_start+2, len(line)) > -1:
                    sub_string = line[notes_start:line.find('*/', notes_start+2, len(line)) + 2]
                    line = line.replace(sub_string, '')
                    continue
                else:  # */在下一行,删除/*后面的东西
                    line = line[:notes_start]
                    is_notes = True
                    break
        start = line.find("//")  # 删除"/**/"注释和字符串后面的“//”注释
        if start > -1:
            line = line[:start]

        line = line.strip()  # 去掉两端的空格
        if line != "":
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
                    if data[2]=='None':
                        data[2]=data[1] #第三项为“”None则直接使用第1，0项作为key，value(key不能相同，所以用第二项作为key)
                        data[1]=data[0]
                    if node.cur_state==1:
                        node.define_data.append((data[1],(data[2],context[index][1])))
                    else:
                        node.notdefine_data.append((data[1],(data[2],context[index][1])))
                elif data[0]=='ifndef':
                    new_node=Session(data[1])
                    new_node.cur_state=2
                    if node.cur_state==1:
                        node.define_list.append(new_node)
                    else:
                        node.notdefine_list.append(new_node)
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif data[0]=='ifdef':
                    new_node=Session(data[1])
                    new_node.cur_state=1
                    if node.cur_state==1:
                        node.define_list.append(new_node)
                    else:
                        node.notdefine_list.append(new_node)
                    stack.append(node)
                    stack.append(new_node)
                    break
                elif data[0]=='else':
                    if node.cur_state==1:
                        node.cur_state=2
                    elif node.cur_state==2:
                        node.cur_state=1

                index += 1
                data = split_string(context[index][0])
            index += 1

        self._dump_dict={}
        self._convert_session_datas(root, self._pre_define_macros)


    def preDefine(self,s):
        """
        Macros predefined

        :param s:Pre-defined macro string,split with ";" of macros
        :return:None
        """
        self._pre_define_macros=[]
        macros=s.split(';')
        for item in macros:
            if item.strip()!='':
                self._pre_define_macros.append(item)


    def dumpDict(self):
        """
        Resolve all available macro to a dict

        :return:dict
        """
        return self._dump_dict

    def dump(self,f):
        """
        Output all available macros stored in the new Cpp file

        :param f:file path
        :return:None
        """
        pass




if __name__ == "__main__":
    a1 = PyMacroParser()
    a2 = PyMacroParser()
    a1.load("a2.cpp")
    print a1.dumpDict()
    # print '-------------------------'
    # a1.preDefine("MC1;MC2")
    # a1.load("a2.cpp")
    # print a1.dumpDict()
    # print '-------------------------'
    # a1.preDefine("")
    # a1.load("a2.cpp")
    # print a1.dumpDict()

    # filename = "b.cpp"
    # a1.dump(filename)  # 没有预定义宏的情况下，dump cpp
    # a2.load(filename)
    # print a2.dumpDict()
    # a1.preDefine("MC1;MC2")  # 指定预定义宏，再dump
    # a1.dumpDict()
    # a1.dump("c.cpp")

    






