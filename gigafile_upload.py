from playwright.sync_api import sync_playwright
import sys
import os
import time
import pyperclip

print("ギガファイル便自動アップロードスクリプト v1.0\n")
print("1.ファイルをアップロードする\n")
print("2.アップロードしたファイルのURLを表示\n")
print("3.アップロードしたファイルの削除\n")
print("制作者：Himarry\n\n")

# アップロードしたファイル情報を保存するファイル
INFO_FILE = "uploaded_file_info.txt"

FILE_PATH = ""
term_choice = "2"

while True:
    choice = input("操作を選択してください（1-3, 終了はq）: ").strip()
    if choice == "1":
        FILE_PATH = input("アップロードするファイルのパスを入力してください: ").strip().strip('"')
        if not FILE_PATH:
            print("ファイルパスが入力されませんでした。\n")
            continue
        # 保持期限選択
        print("保持期限を選択してください")
        print("1.3日\n2.5日（デフォルト）\n3.7日\n4.14日\n5.30日\n6.60日\n7.100日")
        term_choice = input("番号を入力してください（1-7、未入力は2）: ").strip()
        if term_choice not in ["1","2","3","4","5","6","7",""]:
            print("無効な入力です。5日（デフォルト）で進めます。\n")
            term_choice = "2"
        if term_choice == "":
            term_choice = "2"
        break
    elif choice == "2":
        # URL表示機能
        try:
            with open(INFO_FILE, "r", encoding="utf-8") as f:
                info = f.read()
            print("\n=== アップロード済みファイル情報 ===")
            print(info)
            print("==============================\n")
        except FileNotFoundError:
            print("アップロード済みファイル情報が見つかりません。\n")
    elif choice == "3":
        # 削除機能（ファイル情報のみ削除）
        if os.path.exists(INFO_FILE):
            os.remove(INFO_FILE)
            print("アップロード済みファイル情報を削除しました。\n")
        else:
            print("削除するファイル情報がありません。\n")
    elif choice.lower() == "q":
        print("終了します。")
        exit()
    else:
        print("1〜3の数字、またはqを入力してください。\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://gigafile.nu/", timeout=120000)

    # 保持期限のliタグをクリック
    term_map = {"1": "3", "2": "5", "3": "7", "4": "14", "5": "30", "6": "60", "7": "100"}
    page.click(f'li[data-lifetime-val="{term_map[term_choice]}"]')
    time.sleep(0.5)

    # input[type="file"] を探してファイルをセット
    page.set_input_files('input[type="file"]', FILE_PATH)
    time.sleep(1)

    # アップロード完了まで「完了！」ステータスを待つ（ループで監視）
    for _ in range(120):  # 最大2分間監視
        status = page.query_selector('span.status').inner_text()
        if "完了" in status:
            break
        time.sleep(1)
    else:
        print("アップロードが2分以内に完了しませんでした。\n")

    # ダウンロードURL取得（origin属性から取得）
    url = page.query_selector('input.file_info_url.url').get_attribute('origin')
    # ダウンロード期限取得
    term = page.query_selector('span.download_term_value').inner_text()
    # ステータス取得
    status = page.query_selector('span.status').inner_text()

    print("ダウンロードURL:", url)
    print("ダウンロード期限:", term)
    print("ステータス:", status)

    # URLをクリップボードにコピー
    if url:
        pyperclip.copy(url)
        print("ダウンロードURLをクリップボードにコピーしました。\n")
    else:
        print("ダウンロードURLが取得できませんでした。\n")

    # ファイル情報を保存（追記モード）
    with open(INFO_FILE, "a", encoding="utf-8") as f:
        f.write(f"ファイル: {FILE_PATH}\nダウンロードURL: {url}\nダウンロード期限: {term}\nステータス: {status}\n\n")

    browser.close()
