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
        self._root=None
        self._dump_dict={}

    def _strtotuple(self,tup_str):
        s,real_str=tup_str
        temp_str = []
        for i in real_str:
            temp_str.append(i)
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
                if i == ',' or index==len(s):
                    if index==len(s) and i!=',':
                        data = s[start:]
                    else:
                       data=s[start:index-1]
                    node_finished=False
                    if data.find('}')>-1:
                        data=data.replace('}','')
                        node_finished=True
                    while data.find('$')>-1 and len(temp_str)>0:
                        replace_index=data.find('$')
                        data=data[:replace_index] + temp_str.pop(0) + data[replace_index + 1:]
                    node.data.append(self._convert_rest(data))
                    start=index
                    if node_finished==True:
                        break
                elif i=='{':
                    new_node=TupleData()
                    node.data.append(new_node)
                    start=index
                    stack.append(node)
                    stack.append(new_node)
                    break
                if index==len(s) and s[-1]==',':
                    node.data.append(self._convert_rest(''))
        return self._resolve_tuple_data(root)

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
                start=v.find('{')
                end=v.rfind('}')
                if end==-1 or end<start:
                    raise Exception('missing }')
                return self._strtotuple((v[start+1:end],temp_v))

            #把保存的字符串还原
            while v.find('$') > -1:
                replace_index = v.find('$')
                v = v[:replace_index] + temp_v.pop(0) + v[replace_index + 1:]
            return self._convert_rest(v)
        except :
            raise


    def _convert_rest(self, v):
        v=v.strip()
        if v=='':
            return None
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
            return v.decode('utf-8') #encode('string_escape')

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

        # 转换有l的浮点型
        if v.find("\"") == -1 and v.find('{') == -1 and v.find('l') > -1:
            return string.atof(self._sign_strip(v.replace('l', '')))

        # 转换有L的浮点型
        if v.find("\"") == -1 and v.find('{') == -1 and v.find('L') > -1:
            return string.atof(self._sign_strip(v.replace('L', '')))

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

    def _convert_session_datas(self, node, defindString, dump_dict):
        index = defindString.count(node.key)
        if index > 0:
            for item in node.define_data:
                if isinstance(item,Session):
                    self._convert_session_datas(item, defindString, dump_dict)
                else:
                    k, (v, real_str)=item
                    if k == 'define':
                        if defindString.count(v) == 0:
                            defindString.append(v)
                            dump_dict[v]= None
                    elif k == 'undef':
                        if defindString.count(v) > 0:
                            defindString.remove(v)
                        if dump_dict.has_key(v):
                            del dump_dict[v]
                    else :
                        dump_dict[k]=self._convert_cpp_to_python((v, real_str))

        else:
            for item in node.notdefine_data:
                if isinstance(item,Session):
                    self._convert_session_datas(item, defindString, dump_dict)
                else:
                    k, (v, real_str)=item
                    if k == 'define':
                        if defindString.count(v) == 0:
                            defindString.append(v)
                            dump_dict[v]= None
                    elif k == 'undef':
                        if defindString.count(v) > 0:
                            defindString.remove(v)
                        if dump_dict.has_key(v):
                            del dump_dict[v]
                    else :
                        dump_dict[k]=self._convert_cpp_to_python((v, real_str))


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
                            line=line.replace(line[0:end+2]," ")
                            is_notes=False
                        else:  #当前行还是注释行，跳过
                            line = p.readline()
                            continue
                    is_notes=self.remove_notes(context,line)
                    line=p.readline()
        except :
             raise
        return context

    def _my_replace(self,line,start,end,save_list,placeholder):
        sub_string = line[start:end + 1]
        save_list.append(sub_string)
        return  line.replace(sub_string, placeholder)


    def _replace_string(self,line,old_string):
        start=0
        end = start
        state=0   #0表示没有匹配，1：正在匹配“”，2：正在匹配‘’，3：正在匹配/**/ ，4：正在匹配转义符\
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
                elif i=='\\':
                    state=4
            else:
                if state==1 and i=='\"' and old_char!='\\':#结束匹配
                    line = self._my_replace(line, start, end,  old_string,'$')
                    state=0
                    return self._replace_string(line, old_string)
                elif state==2 and i=='\''and old_char!='\\':
                    line = self._my_replace(line,start,end,old_string,'$')
                    state=0
                    return self._replace_string(line, old_string)
                elif state==3 and i=='/'and old_char=='*':
                    line = self._my_replace(line, start, end, [], ' ')
                    state=0
                    return self._replace_string(line, old_string)
                elif state==4:
                    old_char=''
                    state=0
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

        # 屏蔽掉字符串，删除注释后再插入原来的位置（TODO?并且把转义字符转成相应的字符）
        old_string = []  # 里面的项为(原字符串),在去除掉注释后再插入
        line,is_notes=self._replace_string(line,old_string)

        if is_notes:
            start=line.find("/*")
            if start>-1:
                line=line[:start]
        start = line.find("//")  # 删除"/**/"注释和字符串后面的“//”注释
        if start > -1:
            line = line[:start]

        start = line.find(";")  # 删除；后面的内容
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
        try:
            self._dump_dict={}
            self._convert_session_datas(self._root, self._pre_define_macros, self._dump_dict)
        except:
            raise


    def preDefine(self,s):
        """
        Macros predefined

        :param s:Pre-defined macro string,split with ";" of macros
        :return:None
        """
        self._pre_define_macros=[]
        self._dump_dict={}
        macros=s.split(';')
        for item in macros:
            if item.strip()!='':
                self._pre_define_macros.append(item)
                self._dump_dict[item]=None

        try:
            self._convert_session_datas(self._root, self._pre_define_macros, self._dump_dict)
        except:
            raise

    def dumpDict(self):
        """
        Resolve all available macro to a dict

        :return:dict
        """
        dump_dict =self._deepcopy(self._dump_dict)
        return dump_dict

    def _deepcopy(self, src_dict):
        res={}
        for k,v in src_dict.items():
            if isinstance(v,dict):
                res[k]=self._deepcopy(v)
            else:
                res[k]=v
        return res

    def dump(self,f):
        """
        Output all available macros stored in the new Cpp file

        :param f:file path
        :return:None
        """
        try:
            with open(f, 'w') as p:
                for k,v in self._dump_dict.items():
                    if self.is_w_string(v):
                        v = "L\"" + v + "\""
                    elif self._is_string(v):
                        v="\""+v+"\""
                    elif v is False:
                        v='false'
                    elif v is True:
                        v='true'
                    elif v is None:
                        v=''
                    elif self._is_tuple(v):
                        old_string=[]
                        v=self._remove_string(v,old_string)
                        v = v.replace('(', '{')
                        v = v.replace(')', '}')
                        start=v.find('$',0,len(v))
                        while start>-1:
                            v=v[:start]+'\"'+old_string.pop(0)+'\"'+v[start+1:]
                            start = v.find('$',start, len(v))
                    p.write('#define '+str(k)+' '+ str(v)+'\n')
        except :
             raise

    def _remove_string(self,v,old_string):
        for i in v:
            if self._is_string(i):
                old_string.append(i)
            elif self._is_tuple(i):
                self._remove_string(i,old_string)
        v=str(tuple(v))
        while v.find('\'')>-1:
            start=v.find('\'')
            end=v.find('\'',start+1,len(v))
            if end>start:
                sub=v[start:end+1]
                v=v.replace(sub,'$')
        while v.find('\'')>-1:
            start=v.find('\'')
            end=v.find('\'',start+1,len(v))
            if end>start:
                sub = v[start:end + 1]
                v = v.replace(sub, '$')
        return v
    def _is_tuple(self,obj):
        try:
            return isinstance(obj,tuple)
        except:
            return False
    def is_w_string(self,obj):
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
    a2 = PyMacroParser()
    a1.load("a2.cpp")
    filename = "b.cpp"
    a1.dump(filename)  # 没有预定义宏的情况下，dump cpp
    a2.load(filename)
    for k,v in a2.dumpDict().items():
        print k,":",v

    # print '---------'
    #
    # a1.load("b.cpp")
    # a1.dump("d.cpp")
    # for k, v in a1.dumpDict().items():
    #     print k, ":", v


    # a1.preDefine("MC1;MC2")  # 指定预定义宏，再dump
    # print  a1.dumpDict()
    # a1.dump("c.cpp")
    #
    # a1.preDefine("   \f\n\r\tMC1; \t\\MC2; \v\vMC3\t; \fMC4")
    # print a1.dumpDict()

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

    






