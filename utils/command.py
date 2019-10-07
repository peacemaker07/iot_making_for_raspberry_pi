# ドキュメント：https://docs.python.jp/3.5/library/subprocess.html?highlight=subprocess

from subprocess import Popen, PIPE, run


class Command:
    """
    コマンドの送信を行うクラス
    """

    RET_CD_OK = 0  # コマンド送信成功

    @staticmethod
    def cmd_run(cmd_list, cmd_input=None, shell=False):
        """
        新しいプロセスでコマンドを実行する
        :param cmd_list: 実行するコマンド（リスト）
        :param cmd_input: 応答する内容
        :param shell: cmd_listが文字列の場合、Trueとする（非推奨）
        :return: 処理結果（True：成功、False：失敗）、
                 成功時のレスポンス（binary）、
                 失敗時のレスポンス（binary）
        """
        # コマンドを実行する
        p = Popen(cmd_list, shell=shell, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        # プロセスとの通信: データを標準入力に送る
        stdout_data, stderr_data = p.communicate(input=cmd_input)

        if p.returncode != Command.RET_CD_OK:
            return False, stdout_data, stderr_data

        return True, stdout_data, stderr_data

    @staticmethod
    def shell_run(cmd_list):
        """
        コマンドを実行する
        :param cmd_list: 実行するコマンド（リスト）
        :return: なし
        """
        run(cmd_list)
