import os
import sys
import subprocess
import pyclamd
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog, Tk, Label
from tkinter.ttk import Progressbar
from pygments.lexers import guess_lexer, get_lexer_for_filename
from pygments.util import ClassNotFound
from io import StringIO

MASTER_ID = "admin"
MASTER_PASS = "password123"
SUPPORTED_LANGUAGES = ["Python", "VB.NET", "FORTRAN", "Java", "JavaScript", "C", "C++", "C#", "VB6", "VBA"]

def authenticate():
    root = Tk()
    root.withdraw()
    try:
        user_id = simpledialog.askstring("ログイン", "IDを入力してください:")
        user_pass = simpledialog.askstring("ログイン", "パスワードを入力してください:", show="*")
    except Exception as e:
        messagebox.showerror("エラー", f"認証に失敗しました: {e}")
        sys.exit()

    if user_id == MASTER_ID and user_pass == MASTER_PASS:
        messagebox.showinfo("ログイン成功", "ようこそ、管理者様。")
        return True
    else:
        messagebox.showwarning("閲覧モード", "ID/PASSが無効です。閲覧モードで起動します。")
        return False

def select_directory():
    root = Tk()
    root.withdraw()
    try:
        folder_path = filedialog.askdirectory(title="解析するフォルダを選択してください")
    except Exception as e:
        messagebox.showerror("エラー", f"フォルダ選択に失敗しました: {e}")
        sys.exit()

    if not folder_path:
        messagebox.showerror("エラー", "フォルダが選択されていません")
        sys.exit()
    return folder_path

def scan_for_virus(file_path):
    try:
        cd = pyclamd.ClamdAgnostic()
        if not cd.ping():
            return "ClamAVが起動していません"
        result = cd.scan_file(file_path)
        return f"ウイルス検知: {result}" if result else "なし"
    except Exception as e:
        return f"スキャンエラー: {e}"

def check_syntax(file_path, content, language):
    try:
        if language == "Python":
            compile(content, file_path, 'exec')
            return "なし"
        elif language == "VB.NET":
            result = subprocess.run(["vbc", file_path], capture_output=True, text=True)
            return result.stderr if result.returncode != 0 else "なし"
        elif language == "FORTRAN":
            result = subprocess.run(["gfortran", "-fsyntax-only", file_path], capture_output=True, text=True)
            return result.stderr if result.returncode != 0 else "なし"
        elif language in ["VB6", "VBA"]:
            return "構文チェック未対応"
        elif language == "JavaScript":
            return "一部構文チェック未対応"
        else:
            return "構文チェック未対応"
    except Exception as e:
        return f"構文チェックエラー: {e}"

def analyze_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception:
        return None

    try:
        lexer = get_lexer_for_filename(file_path)
        language = lexer.name
    except:
        try:
            lexer = guess_lexer(content)
            language = lexer.name
        except:
            return None

    if language not in SUPPORTED_LANGUAGES:
        return None

    report = f"=== {file_path} ===\n"
    report += f"- 言語: {language}\n"

    if "社外秘" in content or "極秘" in content:
        report += "⚠️ このファイルには機密情報の可能性があります\n"

    virus_status = scan_for_virus(file_path)
    if "ウイルス検知" in virus_status:
        return f"{file_path} はウイルスの可能性があります！\n{virus_status}\n"

    syntax_result = check_syntax(file_path, content, language)
    if syntax_result != "なし":
        report += f"- 構文エラー: {syntax_result}\n"
        return report

    return None

def analyze_directory(directory):
    report = StringIO()
    files = [os.path.join(root, f) for root, _, fs in os.walk(directory) for f in fs]
    progress = tk.Tk()
    progress.title("解析中")
    label = Label(progress, text="解析中...")
    label.pack()
    bar = Progressbar(progress, orient="horizontal", length=300, mode="determinate")
    bar.pack(pady=10)
    bar["maximum"] = len(files)

    for idx, file in enumerate(files):
        bar["value"] = idx + 1
        label.config(text=f"{os.path.basename(file)} を解析中...")
        progress.update()
        result = analyze_file(file)
        if result:
            report.write(result + "\n\n")

    progress.destroy()

    if report.getvalue():
        result_path = os.path.join(directory, "解析結果.txt")
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(report.getvalue())
        messagebox.showinfo("完了", f"解析完了\n出力: {result_path}")
    else:
        messagebox.showinfo("完了", "解析は完了しましたが、出力するエラーはありません。")

if __name__ == "__main__":
    is_admin = authenticate()
    selected_dir = select_directory()
    analyze_directory(selected_dir)
