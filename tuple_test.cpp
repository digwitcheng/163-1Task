#ifndef MCTEST
#define /**/MCTEST

#ifdef MC1


//#define da11 {1,2,'' /*,{},*/};
//
//#define da7 {+0x22,-'0x23',+'0x55',"\000",}
//#define oct1 016
//
///*dksfnhj*/ #define data27 {'}{',"{}}{",}
//#/*dksfnhj*/ define data26 {"{\\}" , {/*"
////"''*/ } , - +2.0f, "abc"  ,{ '\\\'',"def"},5.6f,"h/**/lo", '//', {"#define",.5e2}} // 浮点与字符串组成的结构体初始化聚合， 再进一步聚合组成了数组

#define str20 "24\'23\'t323df"
#define str21 "ABCDEFGHIJKL" "MNOPQRSTUVWY"
#define str22 "\x41\102\103DEFG"/*fdsfdfdfd*/"HI\JKLMNO\PQ\RSTUVW\X\Z\bYZ\b\012"
#define X "\\\\\\\\\\\\\\\\\\\\A//////////"

#define data1  /* this is float
may be changed
*/+0x0e
#define data2  /* this is float
may be changed
*/016

#ifdef MC2

#define da{}  { 1, }
#define da2 {{{1}}}
#define da3     {{1},{2,},/*/*/}
#define A '\x22\134'

#else

#define da4 {,}
#define da44 {1,}

#endif //end MC2


#define da1 {}
#define da2 { {,,,,}}
#define da3 { 1 , { 2 , } , { 3, 4 , } }
#define da4 {,}
#define da5 {,{},}
#define da6 {,{},{}}

#else

#define da1 {1,2,"/**/"};;
#define   aaa { 1,2,'\00'}; {};

#endif //MC1

#ifdef MC2
#undef MC2
#undef
#else niha  ee
#define eee
#endif // !MC_TEST