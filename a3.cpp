#ifndef MCTEST
#define MCTEST


#ifdef MC1

//#define d3 L"this is"" a data"
//#define d4 {L"this is"" a data"}
//#define d5 L"this is" ## " a data"
//#define d6 "this is" ## " a data"
//#define d7 {L"this is" ## " a data"}
//#define d8  " a data  "

//#define charc3 L"\\"
//#define charc2 "\""
//#define charc4 "}1{\\"
//#define charc "\\\""//"':"'/\*/
//#define A '\x22\134'
//#define charc5 '\\\''
//#define charc6 "\"\\"
//#define Float 2.3E-3

//#define data22 {{'a\''}, '\\',{'\"'} }
////#define data20/**/{ {2.0, "abc"}, {1.5, "def"}, {5.6f, "7.2"}}
////#define data26 {{"{\\}"} , {/*"//"''*/ } , {- +2.0f, "abc" } ,{ '\\\'',"def"},{5.6f,"h/**/lo", '//'}, {"#define",.5e2}} // 浮点与字符串组成的结构体初始化聚合， 再进一步聚合组成了数组
////#define data21 {{"{\'}\\"}  ,{'{}'},};
////#define data23 {{{{{}}}}}
//#define data25 {{ 2 ,  3 },{},,}
//#define data27 {'}{',"{}}{",}
//#define data28 {3,"",4}
//#define data29 {}{, , ,/*{}*/,1}
//#/*dksfnhj*/ define  MCT/*f dhsdjklflk*/ {"}1{\\",/*fdhfhfdf*/{},"}1{",}

#define da1 {}
#define da2 {{,,,,}}
#define da3 {{},{}}
#define da4 {,}
#define da5 {,{},}
#define da6 {,{},{}}
#define da7{+0x22,-'0x23',+'0x55',-\000,}
#define da8 {'cc',',','c','\b','\x22','"'}
#define da9 {,{'\x0','\x1','\x2'}}

#ifdef MC2

//#define data4 true
//#define data1 123
//#define data152 "asdb"##"dfalkj" ;123
//#define data151 "abc" ;"123"

#else
//#define data5 {5.0, 7.5, 3.8}
//#define data6 'c'

#endif //end MC2

#else
//#define xx "XXX \\tYYY\nZZZZ \n"
//#define data13 20u
//
//#define data30 '\077a'
//#define data31 '\x3at'
//#define data32 "\bc\x097\a\x3Ft\f\n\r\ta"
//#define data15 '{}'
//#define data16 {/*""/\\\*/ 3.3,'//',"/*///''",.2e2f}
////#define comment/**/" #define A /*+-*/"@RaAlGhul
//#define data17 123e-4
//#define data18 12
//
//#define abc " ab\tc "  ##  " d\\d "
//#define data1  .1e2f
///*cmment start*/#define /*this is comment*/ data2 .5e2f;;;;;
//#define date3 L"this is a data"


////#/*dksfnhj*/ define  MCT/*f dhs{{}lflk */ {"}}",'{}{',"}1{\\",/*fdhfhfdf*/{},"}1{",}
//#define da7 {+0x22,-'0x23',+'0x55',-\000,};
//#define da8 {'cc',',','c','\b','\x22','\x00','"'}
//#define da10 {\x001,'"'}
//#define A '\xff'
//#define data41 12.03L
#define     data41 12.03L///*
#define data42/*/*/1.f//*/
#define data43/*/*/10.2E-10f///*
#define data44 "\\\\\"\\'\"\\\////////'/'//''////"
#define data45 '\\b'
#define String/*666*/12
#define data46 "\'\"/**/\\\'"
#define data47 "\'\""/**/"\\\'"
#define data48 "\'\"" ##"/**/\\\'"
#define data49 {"\'\"" ##"/**/\\\'"}
#define data50 {"\'\""  "/**/\\\'"}


//#define da88 {"cc",",","c","\b","\x22","'"}
//#define da9 {,{'\x02','\x01','\x02'}}


//#define da7 {+0x22,-'0x23',+'0x55',-\000,};
//#define da8 {'cc',',','c','\b','\x22','"'}
//#define da88 {"cc",",","c","\b","\x22","'"}
//#define da9 {,{'\x02','\x01','\x02'}}

#define data22 {{'a\''}, '\\',{'\"'} }
#define data20/**/{ {2.0, "abc"}, {1.5, "def"}, {5.6f, "7.2"}}
#define data26 {{"{\\}"} , {/*"//"''*/ } , {- +2.0f, "abc" } ,{ '\\\'',"def"},{5.6f,"h/**/lo", '//'}, {"#define",.5e2}} // 浮点与字符串组成的结构体初始化聚合， 再进一步聚合组成了数组
#define data21 {{"{\'}\\"}  ,{'{}'},};
#define data23 {{{{{}}}}}
#define data25 {{ 2 ,  3 },{},,}
#define data27 {}
#define data28 {3,,4}
#define data29 {,,1}
#/*dksfnhj*/ define  MCT/*f dhsdjklflk*/ {"}1{\\",/*fdhfhfdf*/{},"}1{",}

#endif //MC1

#ifdef MC2
#undef MC2
#endif

#endif // !MC_TEST