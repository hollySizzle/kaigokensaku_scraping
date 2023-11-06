# -*- coding: utf-8 -*-
import requests
from requests_html import HTMLSession
import pandas as pd
import logging
import re  # 正規表現モジュールをインポート
import time

# import pykakasi
# kakasi = pykakasi.kakasi() # インスタンスの作成
# kakasi.setMode('H', 'a') # ひらがなをローマ字に変換するように設定
# kakasi.setMode('K', 'a') # カタカナをローマ字に変換するように設定
# kakasi.setMode('J', 'a') # 漢字をローマ字に変換するように設定
# conversion = kakasi.getConverter() # 上記モード設定の適用


# JavaScriptをレンダリングする関数
def scrape_html(url, sleep_sec, timeout_sec=60):
    try:
        session = HTMLSession()
        r = session.get(url)
        # r.html.render(sleep=sleep_sec, timeout=timeout_sec)

        # # r.html.find("body", first=True)を"sample.html"という名前で保存する
        # with open("sample.html", mode="w", encoding="utf-8") as f:
        #     f.write(r.html.find("body", first=True).html)

        return r.html.find("body", first=True)

    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
        logging.error(f"リクエストエラー: {e}")
        return "error"

    except Exception as e:
        print(f"その他のエラー: {e}")
        logging.error(f"その他のエラー: {e}")
        return "error"


# HTML要素を解析する関数
def purse_html(elements):
    # 例 https://www.kaigokensaku.mhlw.go.jp/27/index.php?action_kouhyou_detail_021_kihon=true&JigyosyoCd=2791100478-00&ServiceCd=730
    if elements is None:
        return "error"

    site_contents = elements

    dataset = {}

    url = site_contents.url
    # idをdata-jigyosyocdから取得する
    id_html = site_contents.find(
        "#kihonPage > div > div.col.order-2 > article > section > div.position-relative.jigyoshoShosai > div > ul > li:nth-child(2) > a"
    )[0].html

    # <a data-versioncd="004">からdata-jigyosyocdを取り出す
    id = id_html.split('data-jigyosyocd="')[1].split('"')[0]

    dataset["data-id"] = id
    dataset["url_詳細"] = url

    dataset["事業所の名称"] = site_contents.find(
        "#kihonPage > div.row > div.col.order-2 > article > section > div.position-relative.jigyoshoShosai > h1"
    )[0].text

    # shozaichiBlock > div > div から起票日をtext取り出し､datasetに格納する｡
    dataset["起票日"] = site_contents.find("#shozaichiBlock > div > div")[0].text.split(
        "："
    )[1]

    # id=check_CorporateNumber から法人番号をtext取り出し､datasetに格納する｡
    # もしなければ"-"をdatasetに格納する｡"
    try:
        dataset["法人番号"] = site_contents.find("#check_CorporateNumber")[0].text
    except:
        dataset["法人番号"] = "-"

    # tableGroup-1の中のtableのhtmlを取り出す
    # なぜかtbodyは取り出せない(表示の際には自動で追加される)
    info_table = site_contents.find("#tableGroup-1 > table:nth-child(1)")[0]

    # info_tableから法人番号の取り出しと格納
    dataset["法人等の名称"] = info_table.find("tr:nth-child(5) > td")[0].text

    # info_tableから法人名のふりがなを取り出し､datasetに格納する｡
    dataset["法人等の名称_ふりがな"] = info_table.find("tr:nth-child(4) > td")[0].text

    # info_tableからtr:nth-child(13) > td から 法人等の代表者の氏名を取り出し､datasetに格納する｡
    dataset["法人等の代表者の氏名"] = info_table.find("tr:nth-child(13) > td")[0].text

    # info_tableからtr:nth-child(8) > td.houjin_number_check から 法人等の主たる事務所の所在地_郵便番号を取り出し､datasetに格納する｡
    # 格納の際に､"〒"と"-"を削除し､半角に変換し､Int型として格納する｡
    dataset["法人等の主たる事務所の所在地_郵便番号"] = (
        info_table.find("tr:nth-child(8) > td.houjin_number_check")[0]
        .text.replace("〒", "")
        .replace("-", "")
        .replace("ー", "")
        .replace("−", "")
    )

    # info_tableからtr:nth-child(9) > td から 事業所名の所在地を取り出し､datasetに格納する｡
    dataset["法人等の主たる事務所の所在地"] = info_table.find("tr:nth-child(9) > td")[0].text

    # info_tableからtr:nth-child(10) > td から 法人等の連絡先 を取り出し､datasetに格納する｡
    # 格納の際に､"-"を削除し､半角に変換し､Int型として格納する｡
    dataset["法人等の連絡先"] = (
        info_table.find("tr:nth-child(10) > td")[0]
        .text.replace("-", "")
        .replace("ー", "")
        .replace("−", "")
    )

    # info_tableからtr:nth-child(10) > td から 法人等の連絡先 を取り出し､datasetに格納する｡
    # 格納の際に､"-"を削除し､半角に変換し､Int型として格納する｡
    dataset["FAX番号"] = (
        info_table.find("tr:nth-child(11) > td")[0]
        .text.replace("-", "")
        .replace("ー", "")
        .replace("−", "")
    )
    # info_tableからtr:nth-child(10) > td から 法人等の連絡先 を取り出し､datasetに格納する｡
    # 格納の際に､"-"を削除し､半角に変換し､Int型として格納する｡
    dataset["tel_fax"] = site_contents.find(
        "#shozaichiBlock > div > table > tbody:nth-child(3) > tr > td > div:nth-child(1)"
    )[0].text

    # info_tableからtr:nth-child(12) > td から ホームページを取り出し､datasetに格納する｡
    # urlがない場合は"-"を格納する｡
    if info_table.find("tr:nth-child(12) > td > div")[0].text == "":
        dataset["ホームページ"] = "-"
    else:
        dataset["ホームページ"] = info_table.find("tr:nth-child(12) > td > div")[0].text

    return dataset


# toDo tr の順番がめちゃくちゃなので後で考える
def purse_html_kihon(dataset, elements):
    if elements is None:
        return "error"

    site_contents = elements

    # *********************************************************************************************************************
    # 事業者データ
    # なぜかtbodyは取り出せない(表示の際には自動で追加される)
    # tr:nth-child(hoge)のhogeはデータと取得でズレが発生する｡
    # https://www.kaigokensaku.mhlw.go.jp/27/index.php?action_kouhyou_detail_feature_index=true&JigyosyoCd=2775501758-00&ServiceCd=210

    # tableGroup-3 > table > tr:nth-child(3) > td から 事業所の名称 を取り出し､datasetに格納する｡

    dataset["事業所の所在地"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(3) > td"
    )[0].text

    # tableGroup-3 > table > tr:nth-child(3) > td から 事業所の名称_ふりがな を取り出し､datasetに格納する｡

    dataset["事業所の名称_ふりがな"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(3) > td"
    )[0].text

    # #tableGroup-3 > table > tr:nth-child(4) > th から 郵便番号 を取り出し､datasetに格納する｡
    # 格納の際に､"〒"と"-"を削除し､半角に変換し､Int型として格納する｡

    dataset["事業所の所在地_郵便番号"] = (
        site_contents.find("#tableGroup-3 > table > tr:nth-child(5) > td:nth-child(2)")[
            0
        ]
        .text.replace("〒", "")
        .replace("-", "")
        .replace("ー", "")
        .replace("−", "")
    )

    # #tableGroup-3 > table > tr:nth-child(4) > th:nth-child(3) から 市区町村コード を取り出し､datasetに格納する｡
    dataset["事業所の所在地_市区町村コード"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(5) > th:nth-child(3)"
    )[0].text

    # #tableGroup-3 > table > tr:nth-child(5) > td から 事業所の所在地 を取り出し､datasetに格納する｡
    dataset["事業所の所在地"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(5) > td"
    )[0].text

    # #tableGroup-3 > table > tr:nth-child(7) > td から 法人等の連絡先 を取り出し､datasetに格納する｡
    # 格納の際に､"-"を削除し､半角に変換し､Int型として格納する｡
    dataset["法人等の連絡先"] = (
        site_contents.find("#tableGroup-3 > table > tr:nth-child(7) > td")[0]
        .text.replace("-", "")
        .replace("ー", "")
        .replace("−", "")
    )

    # #tableGroup-3 > table > tr:nth-child(9) > td:nth-child(3) の a href 属性 から 事業所の連絡先_ホームページ を取り出し､datasetに格納する｡
    # urlがない場合は"-"を格納する｡
    if site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(9) > td:nth-child(3) > a"
    ):
        dataset["事業所の連絡先_ホームページ"] = site_contents.find(
            "#tableGroup-3 > table > tr:nth-child(9) > td:nth-child(3) > a"
        )[0].attrs["href"]
    else:
        dataset["事業所の連絡先_ホームページ"] = "-"

    # #tableGroup-3 > table > tr:nth-child(10) > td から 介護保険事業所番号 を取り出し､int型としてdatasetに格納する｡
    print(
        site_contents.find("#tableGroup-3 > table > isRowSpan.tr:nth-child(3)>td")[
            0
        ].html
    )

    exit()
    dataset["介護保険事業所番号"] = int(
        site_contents.find("#tableGroup-3 > table > tr:nth-child(11) > td")[0]
        .text.replace("-", "")
        .replace("ー", "")
        .replace("−", "")
    )

    # #tableGroup-3 > table > tr:nth-child(11) > td から 事業所の管理者の氏名及び職名_氏名 を取り出し､datasetに格納する｡
    dataset["事業所の管理者の氏名及び職名_氏名"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(11) > td"
    )[0].text

    # #tableGroup-3 > table > tr:nth-child(12) > td から 事業所の管理者の氏名及び職名_職名 を取り出し､datasetに格納する｡
    dataset["事業所の管理者の氏名及び職名_職名"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(14) > td"
    )[0].text

    # #tableGroup-3 > table > tr:nth-child(14) > td から 事業の開始（予定）年月日 を取り出し､datasetに格納する｡
    dataset["事業の開始（予定）年月日"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(16) > td"
    )[0].text

    # tableGroup-3 > table > tr:nth-child(15) > td から 指定の年月日 を取り出し､datasetに格納する｡
    dataset["指定の年月日"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(17) > td"
    )[0].text

    # tableGroup-3 > table > tr:nth-child(16) > td から 指定の更新年月日（直近） を取り出し､datasetに格納する｡
    dataset["指定の更新年月日（直近）"] = site_contents.find(
        "#tableGroup-3 > table > tr:nth-child(18) > td"
    )[0].text

    return dataset


def purse_html_feature(dataset, elements):
    if elements is None:
        return "error"

    site_contents = elements

    # *********************************************************************************************************************
    # 特色データ

    # #akisuuValue から 受け入れ可能人数 を取り出し､datasetに格納する｡

    # print(site_contents.url)
    # exit()
    dataset["空き数"] = site_contents.find("#akisuuValue")[0].text

    pattern = r"最大受け入れ人数(.+)人中"

    try:
        dataset["受け入れ可能人数"] = int(
            re.findall(
                pattern,
                site_contents.find(
                    "#ukeireninzuBlock > div > ul > li:nth-child(2) > div"
                )[0].text,
            )[0]
        )
    except:
        dataset["受け入れ可能人数"] = "-"

    return dataset


if __name__ == "__main__":
    print("start")
    xlsx_file = "和歌山_兵庫.xlsx"
    df = pd.read_excel(xlsx_file, header=0, index_col=0)

    last_row = df.shape[0] - 1
    print("最終行番号：", last_row)

    # last_rowの数だけfor文を回す
    for i in range(last_row):
        time_sleep = 0.01
        # time_sleep = 0.5
        # ↑今回は殆ど機能してない

        logging.info("処理:", i + 1, "/", last_row)
        print("処理:", i + 1, "/", last_row)
        # dfの列"処理ステータス"が"yet"でないならば､次のループへ
        if df.loc[i, "処理ステータス"] != "yet":
            continue

        # urlの抜き出しのため､dfの列 "詳細情報を見る" の値を取り出す
        url_kani = df.loc[i, "詳細情報を見る"]

        # **********************************************************
        # 事業所の法人情報

        # 事業所の概要URL取得のため､url_kaniの値から kani を kihon に置換する
        url_kihon = url_kani.replace("kani", "kihon")

        url = url_kihon

        elements = scrape_html(url, time_sleep)

        # elementsが"error"ならば､次のループへ
        if elements == "error":
            df.loc[i, "処理ステータス"] = "error"
            continue

        try:
            dataset = purse_html(elements)
        except:
            df.loc[i, "処理ステータス"] = "error"
            continue
        # dataset = purse_html(elements)

        # **********************************************************
        # 事業所の所在地

        # url = url_kihon

        # elements = scrape_html(url, time_sleep)

        # # elementsが"error"ならば､次のループへ
        # if elements == "error":
        #     df.loc[i, "処理ステータス"] = "error"
        #     df.to_excel(xlsx_file)
        #     continue

        # dataset = purse_html_kihon(dataset, elements)

        # **********************************************************
        # 事業所の特色

        # 事業所の特色 URL取得のため､url の値から {{_数値_}} & kani を feature に置換する

        # urlの値から 021_kani を feature に置換し､url_feature へ格納する
        # 021_kani は 034_kani, 200_kani, 5131_kani など "_" & str(random) & "_kani" の値を取る場合がある
        pattern = r"_\d+_kani"  # 置換対象のパターンを定義
        url_feature = re.sub(
            pattern, "_feature_index", url_kani
        )  # re.sub関数でパターンにマッチする部分を置換

        elements = scrape_html(url_feature, time_sleep)

        # elementsが"error"ならば､次のループへ
        if elements == "error":
            df.loc[i, "処理ステータス"] = "error"
            df.to_excel(xlsx_file)
            continue

        try:
            dataset = purse_html_feature(dataset, elements)
        except:
            df.loc[i, "処理ステータス"] = "error"
            continue

        # # Jsonデータからkeyのリストを作成
        # keys = list(dataset.keys())

        # # keyのリストをカンマ区切りで出力
        # print(",".join(keys))

        # exit()

        # **********************************************************
        # dataset の 保存
        # datasetをforループで回し､dfに格納する｡
        for key, value in dataset.items():
            df.loc[i, key] = value

        # dfの"処理ステータス"を"end"に変更する
        df.loc[i, "処理ステータス"] = "end"

        # 100回ループするごとに､dfを読み込みファイルに上書き保存する
        if i % 100 == 0:
            df.to_excel(xlsx_file)

    # for が終わったら､dfを読み込みファイルに上書き保存する
    df.to_excel(xlsx_file)
