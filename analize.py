import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter.ttk import Progressbar
from pygments.lexers import guess_lexer, get_lexer_for_filename
from pygments.util import ClassNotFound
from io import StringIO
from collections import defaultdict

MASTER_ID = "admin"
MASTER_PASS = "password123"

def authenticate():
    root = tk.Tk()
    root.withdraw()
    user_id = simpledialog.askstring("ログイン", "IDを入力してください:")
    user_pass = simpledialog.askstring("ログイン", "パスワードを入力してください:", show="*")
    if user_id != MASTER_ID or user_pass != MASTER_PASS:
        messagebox.showerror("エラー", "認証失敗。プログラムを終了します。")
        sys.exit()
    messagebox.showinfo("認証成功", "ログイン成功しました。")

def select_directory():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="解析するフォルダを選択してください")
    if not folder_path:
        messagebox.showerror("エラー", "フォルダが選択されていません")
        sys.exit()
    return folder_path

def check_syntax(file_path, content, language):
    try:
        if language == "Python":
            try:
                compile(content, file_path, 'exec')
                return None
            except SyntaxError as e:
                return f"{e.msg} (行 {e.lineno}, 列 {e.offset})"
        elif language == "JavaScript":
            return "文法チェックは限定的です（実行時エラーの可能性あり）"
        elif language == "Java":
            result = subprocess.run(["javac", file_path], capture_output=True, text=True)
            return result.stderr.strip() if result.returncode != 0 else None
        elif language in ["C", "C++"]:
            compiler = "gcc" if language == "C" else "g++"
            result = subprocess.run([compiler, "-fsyntax-only", file_path], capture_output=True, text=True)
            return result.stderr.strip() if result.returncode != 0 else None
        return None
    except Exception as e:
        return f"構文チェック中にエラー: {e}"

def analyze_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            lexer = get_lexer_for_filename(file_path)
            language = lexer.name
        except ClassNotFound:
            try:
                lexer = guess_lexer(content)
                language = lexer.name
            except ClassNotFound:
                language = "不明"

        error = check_syntax(file_path, content, language)
        return language, error

    except Exception as e:
        return "不明", f"ファイル読み込みエラー: {e}"

def analyze_directory(directory):
    all_files = []
    result_by_language = defaultdict(list)

    for root, _, files in os.walk(directory):
        for file in files:
            all_files.append(os.path.join(root, file))

    progress_window = tk.Tk()
    progress_window.title("解析中...")
    progress_label = tk.Label(progress_window, text="ファイルを解析中...")
    progress_label.pack(pady=10)
    progress_bar = Progressbar(progress_window, orient="horizontal", length=300, mode="determinate", maximum=len(all_files))
    progress_bar.pack(pady=10)

    for index, file_path in enumerate(all_files):
        progress_label.config(text=f"解析中: {os.path.basename(file_path)} ({index + 1}/{len(all_files)})")
        progress_bar["value"] = index + 1
        progress_window.update()

        language, error = analyze_file(file_path)
        if error:
            result_by_language[language].append(f"{file_path}\n  エラー: {error}\n")

    progress_window.destroy()

    output_path = os.path.join(directory, "解析結果.txt")
    with open(output_path, 'w', encoding='utf-8') as f:
        for language, reports in result_by_language.items():
            f.write(f"=== {language} の解析結果 ===\n")
            for report in reports:
                f.write(report + "\n")

    messagebox.showinfo("解析完了", f"解析が完了しました\n\n結果ファイル:\n{output_path}")

if __name__ == "__main__":
    authenticate()
    selected_directory = select_directory()
    analyze_directory(selected_directory)
