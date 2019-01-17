# O serviceとしてsolrをインストールする

Y
p69にのっているとおりinstall scriptを実行した。
 ./install_solr_service.sh /opt/solr-7.6.0.tgz

W
```
root@dev:~# ls -la /opt
total 166656
drwxr-xr-x  3 root root      4096 Jan  9 10:20 .
drwxr-xr-x 24 root root      4096 Jan  8 06:26 ..
lrwxrwxrwx  1 root root        15 Jan  9 10:20 solr -> /opt/solr-7.6.0
drwxr-xr-x  9 root root      4096 Jan  9 10:18 solr-7.6.0
-r--r-----  1 root root 170636739 Dec  7 21:53 solr-7.6.0.tgz
root@dev:~# ls /etc/init.d/solr
/etc/init.d/solr
```
ドキュメントどおりに/opt/solrディレクトリと/etc/init.d/solrが作られている

```
root@dev:~# service solr start
root@dev:~# service solr status
● solr.service - LSB: Controls Apache Solr as a Service
   Loaded: loaded (/etc/init.d/solr; generated)
   Active: active (exited) since Wed 2019-01-09 10:27:54 UTC; 6s ago
     Docs: man:systemd-sysv-generator(8)
  Process: 10412 ExecStop=/etc/init.d/solr stop (code=exited, status=0/SUCCESS)
  Process: 10950 ExecStart=/etc/init.d/solr start (code=exited, status=0/SUCCESS)

Jan 09 10:27:50 dev solr[10950]: *** [WARN] *** Your open file limit is currently 1024.
Jan 09 10:27:50 dev solr[10950]:  It should be set to 65000 to avoid operational disruption.
Jan 09 10:27:50 dev solr[10950]:  If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS t
Jan 09 10:27:50 dev solr[10950]: *** [WARN] ***  Your Max Processes Limit is currently 7898.
Jan 09 10:27:50 dev solr[10950]:  It should be set to 65000 to avoid operational disruption.
Jan 09 10:27:50 dev solr[10950]:  If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS t
Jan 09 10:27:54 dev solr[10950]: [146B blob data]
Jan 09 10:27:54 dev solr[10950]: Started Solr server on port 8983 (pid=11016). Happy searching!
Jan 09 10:27:54 dev solr[10950]: [14B blob data]
Jan 09 10:27:54 dev systemd[1]: Started LSB: Controls Apache Solr as a Service.
lines 1-17/17 (END)
```
サービスとしても動いている

T
データを入れる

# ここまでのまとめ
サービスとしてインストールするときは提供されている圧縮ファイルに入っているスクリプトを実行するだけ。ただ、実行するときに圧縮ファイルが必要だから圧縮ファイルをDLしてすぐ消してはダメ。
