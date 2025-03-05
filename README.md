# 論文探索チャットツール
## 概要
本ツールは、論文情報からGraphRAGを用いて構築したDBを基に、チャット形式で論文を探索できるツールです。

## 実行環境
- python 3.10
    - パッケージはrequirements.txtを参照
## 事前準備
1. python_setting.batのPYTHON_EXEC_PATHにこのツールを実行するpythonのパスを指定してください。
2. 実行するpythonの環境で以下を実行して、パッケージをインストールしてください。  
```
>pip install -r requirements.txt
```
3. [DBの更新](#DBの更新)を参考に論文のDBを構築してください。
## 実行
1. chat.batを実行してください。
2. 「api設定」ボタンをクリックして、AzureOpenAIのAPIキーを設定してください。
3. 画面下半分に質問内容を入力し、「send」ボタンを押すとGPTに論文について質問することができます。
4. 画面中央の「search mode」をlocalとglobalに切り替えることで、質問の範囲を切り替えることができます。  
詳細は、GraphRAGの[公式ページ](https://microsoft.github.io/graphrag/query/overview/)を確認してください。

## DBの更新
1. 論文の内容を更新したい場合は、./ragdata/input内のcsvを編集するまたは、新たなcsvファイルを追加してください。  
一度に多くのデータを追加すると、LLMのエラーが出ることがあるので、追加するデータは一度に100件程度にしてください。
2. ./update.batを実行してください。(数時間かかかります。)
