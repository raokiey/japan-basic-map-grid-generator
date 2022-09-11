# 国土基本図の図郭生成スクリプト
オープンデータなどを扱うときにたまに見かける国土基本図の図郭を生成するPythonスクリプトです。  
[「国土数値情報（行政区域データ）」（国土交通省）](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-v2_3.html)の範囲のみ図郭を生成します。  


## 注意事項
- あくまで個人が趣味で開発したものです
- 本ツールを利用したことによって生じたいかなる損害についても、責任を負いかねます


## 使い方
### 実行方法
```shell
python grid_generator.py ${zone} ${level} ${save_dir}
```

### 引数の説明
|引数|型|説明|
|:---:|:---:|:---|
|zone|整数|生成する図郭の平面直角座標系の系番号|
|level|整数|生成する図郭の地図情報レベル<br/>5000、2500、1250、1000、500、250から選択|
|save_dir|文字列|生成した図郭の保存先ディレクトリのパス|

### 生成されるファイルの命名規則
`Zone{系番号}_level{地図情報レベル}` という名前でファイルが生成されます。
ESRI Shapefile形式で出力します。

### 実行例
平面直角座標系8系、地図情報レベル500の図郭（08NE2891など）を作成し、  
直下にある`grid` フォルダに保存。
```shell
python grid_generator.py 8 500 ./grid/
```

## 今後の予定
- [ ] 生成した図郭を表示できるWebアプリケーションの開発

## 参考資料
- 国土基本図の図郭について
    [測量法第34条で定める作業規程の準則　付録７　公共測量標準図式](https://psgsv2.gsi.go.jp/koukyou/jyunsoku/pdf/r2/r2_junsoku_furoku7_0609.pdf)　第84条

- 図郭生成の考え方など
    [こちらのブログ記事](https://qiita.com/shiba54/items/29b8722189fbfe5235cb)を参考にさせて頂きました。
- レベル1250について
    [こちらの資料](https://www.maff.go.jp/j/budget/yosan_kansi/sikkou/tokutei_keihi/seika_H30/ippan/attach/pdf/index-126.pdf)などに記載があったので、公共測量標準図式にはありませんが追加しました。

## License
The source code is licensed MIT,see LICENSE.