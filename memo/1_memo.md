# solr7.5を立ててみる

solrをセットアップして動作を確認する

Y

* java8をダウンロード
* solr7.5をダウンロード
* README通りに ./bin/solr startを実行

W

```
*** [WARN] *** Your open file limit is currently 1024.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
WARNING: Starting Solr as the root user is a security risk and not considered best practice. Exiting.
         Please consult the Reference Guide. To override this check, start with argument '-force'
```

```
vagrant@dev:/opt/solr-7.5.0$ ps aux | grep solr | grep -v grep
vagrant@dev:/opt/solr-7.5.0$
```
solrのプロセスは無い。

→起動していない

T
エラー文を読み解いてみよう

Y
エラー文を読む

W
```
*** [WARN] *** Your open file limit is currently 1024.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
```
なぜか65000であるべき値が1024になっているらしい。

```
WARNING: Starting Solr as the root user is a security risk and not considered best practice. Exiting.
         Please consult the Reference Guide. To override this check, start with argument '-force'
```
セキュリティの観点でrootユーザーでは実行するなとのこと。今回は起動することを優先して'-force'オプションを付けて実行する。

T
solr.in.sh を修正して'-force'オプションで実行する

Y
solr.in.shを修正しようとするも1024となっているところは見当たらない。
かわりにエラー文で書かれていたとおりに
SOLR_ULIMIT_CHECKS=false
と修正した。

```
vagrant@dev:/opt/solr-7.5.0$ sudo ./bin/solr start -force
Waiting up to 180 seconds to see Solr running on port 8983 [\]
Started Solr server on port 8983 (pid=7106). Happy searching!

vagrant@dev:/opt/solr-7.5.0$
```
'-force'をつけて実行してみる。
http://localhost:8983/solr/#/で管理コンソールにアクセスできた！

T
SOLR_ULIMIT_CHECKSが何者かしらべる。
1024と設定されている部分を調べる

Y
1024や7898などのエラー文に出てきた数値でgrepしたが、該当するものが多すぎてよくわからない。
```
vagrant@dev:/opt/solr-7.5.0$ grep -r '1024'
Binary file dist/solrj-lib/commons-math3-3.6.1.jar matches
licenses/apacheds-interceptors-journal-2.0.0-M15.jar.sha1:db0fcdbe5b551604b89ccc7f2e1024f7f5351531
CHANGES.txt:* SOLR-12103: Raise CryptoKeys.DEFAULT_KEYPAIR_LENGTH from 1024 to 2048. (Mark Miller)
・・・
```
エラーにあった文でgrepしてみた。

```
vagrant@dev:/opt/solr-7.5.0$ grep -rH 'open file' | grep -v txt
bin/solr:           echo "*** [WARN] *** Your open file limit is currently $openFiles.  "
bin/solr:      echo "Could not check ulimits for processes and open files, recommended values are"
bin/solr:      echo "     open files:    $SOLR_RECOMMENDED_OPEN_FILES"
vagrant@dev:/opt/solr-7.5.0$
```

W
/opt/solr-7.5.0/bin/solr の中で警告文を出すか判定している

```
openFiles=$(ulimit -n)
       maxProcs=$(ulimit -u)
       if [ $openFiles != "unlimited" ] && [ $openFiles -lt "$SOLR_RECOMMENDED_OPEN_FILES" ]; then
           echo "*** [WARN] *** Your open file limit is currently $openFiles.  "
           echo " It should be set to $SOLR_RECOMMENDED_OPEN_FILES to avoid operational disruption. "
           echo " If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh"
       fi

       if [ $maxProcs != "unlimited" ] && [ $maxProcs -lt "$SOLR_RECOMMENDED_MAX_PROCESSES" ]; then
           echo "*** [WARN] ***  Your Max Processes Limit is currently $maxProcs. "
           echo " It should be set to $SOLR_RECOMMENDED_MAX_PROCESSES to avoid operational disruption. "
           echo " If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh"
       fi
```

ulimitとは、ユーザーに対してシステムリソースがどれぐらい割り当てられているのか取得するコマンド。割り当てられているリソースを見て、チェックをしている。
（ソースから推測）どうもSOLR_RECOMMENDED_OPEN_FILESとか環境変数かulimitでどれぐらいのリソースを使うか設定しておく必要があるみたい
T
solrユーザーを作ってから起動してみる

Y
solrユーザーを作り、solrユーザーなら実行できるようにした。
※一度solrはDLし直した。

```
solr@dev:/opt/solr-7.5.0$ ls -la /opt/solr-7.5.0/
total 1600
drwxr-xr-x  9 root root   4096 Jan  7 18:42 .
drwxr-xr-x  3 root root   4096 Jan  7 18:42 ..
-rwxrw-rw-  1 solr solr 815129 Sep 18 05:59 CHANGES.txt
-rwxrw-rw-  1 solr solr  12646 Sep 14 07:17 LICENSE.txt
-rwxrw-rw-  1 solr solr 694010 Sep 18 05:59 LUCENE_CHANGES.txt
-rwxrw-rw-  1 solr solr  25980 Sep 14 07:17 NOTICE.txt
-rwxrw-rw-  1 solr solr   7490 Sep 14 07:17 README.txt
drwxrw-rw-  3 solr solr   4096 Jan  7 18:47 bin
drwxrw-rw- 11 solr solr   4096 Sep 18 11:08 contrib
drwxr-xr-x  4 root root   4096 Jan  7 18:42 dist
drwxr-xr-x  3 root root   4096 Jan  7 18:42 docs
drwxrw-rw-  6 solr solr   4096 Jan  7 18:42 example
drwxrw-rw-  2 solr solr  36864 Jan  7 18:42 licenses
drwxrw-rw- 11 solr solr   4096 Jan  7 18:47 server
solr@dev:/opt/solr-7.5.0$
```

W
起動できてコンソールが表示された。
```
solr@dev:/opt/solr-7.5.0$  ./bin/solr start
*** [WARN] *** Your open file limit is currently 1024.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 7898.
 It should be set to 65000 to avoid operational disruption.
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
Waiting up to 180 seconds to see Solr running on port 8983 [\]
Started Solr server on port 8983 (pid=14589). Happy searching!
```

ここまでのまとめ

* 基本はダウンロードして展開してbinディレクトリ以下のスクリプトを実行するだけ
* 実行するにはrootではなく専用のユーザーを作っておく必要がある
* solrで使用するシステムリソースを変数で設定していないと警告がでる→実運用だときっちりと決めておかないとリソース不足か過多になる。マシンスペックに合わせて設定しないと。
