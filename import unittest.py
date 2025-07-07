import unittest
from unittest.mock import patch, MagicMock, call
import os
from ler_granito_txt import baixar_txt_e_gerar_csv

# language: python

# Importa a função a ser testada

class TestBaixarTxtEGerarCsv(unittest.TestCase):
    @patch("ler_granito_txt.os")
    @patch("ler_granito_txt.paramiko")
    @patch("ler_granito_txt.gerar_csv_do_txt")
    @patch("ler_granito_txt.os.getenv")
    def test_baixar_txt_e_gerar_csv_baixa_novos_txts(self, mock_getenv, mock_gerar_csv, mock_paramiko, mock_os):
        # Configura variáveis de ambiente simuladas
        mock_getenv.side_effect = lambda key, default=None: {
            "SFTP_HOST": "fake_host",
            "SFTP_PORT": "22",
            "SFTP_USER": "user",
            "SFTP_PASS": "pass",
            "SFTP_REMOTE_DIR": "/remote",
            "TXT_DIR": "./local_txt",
            "CSV_DIR": "./local_csv"
        }.get(key, default)

        # Simula arquivos locais e remotos
        mock_os.listdir.side_effect = [
            ["file1.csv"],  # arquivos já processados na pasta CSV
        ]
        mock_os.path.splitext.side_effect = lambda f: os.path.splitext(f)
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.makedirs.return_value = None

        # Simula arquivos remotos
        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_paramiko.Transport.return_value = mock_transport
        mock_paramiko.SFTPClient.from_transport.return_value = mock_sftp
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_sftp.chdir.return_value = None

        # Simula arquivos já processados
        # file1.csv já existe, então só file2.txt é novo
        # file1.txt já processado, file2.txt não
        mock_gerar_csv.reset_mock()

        baixar_txt_e_gerar_csv()

        # Verifica se só file2.txt foi baixado e processado
        mock_sftp.get.assert_called_once_with("/remote/file2.txt", "./local_txt/file2.txt")
        mock_gerar_csv.assert_called_once_with("./local_txt/file2.txt", "./local_csv")
        mock_sftp.close.assert_called()
        mock_transport.close.assert_called()

    @patch("ler_granito_txt.os")
    @patch("ler_granito_txt.paramiko")
    @patch("ler_granito_txt.gerar_csv_do_txt")
    @patch("ler_granito_txt.os.getenv")
    def test_baixar_txt_e_gerar_csv_sem_novos_txts(self, mock_getenv, mock_gerar_csv, mock_paramiko, mock_os):
        mock_getenv.side_effect = lambda key, default=None: {
            "SFTP_HOST": "fake_host",
            "SFTP_PORT": "22",
            "SFTP_USER": "user",
            "SFTP_PASS": "pass",
            "SFTP_REMOTE_DIR": "/remote",
            "TXT_DIR": "./local_txt",
            "CSV_DIR": "./local_csv"
        }.get(key, default)

        mock_os.listdir.side_effect = [
            ["file1.csv", "file2.csv"],  # arquivos já processados
        ]
        mock_os.path.splitext.side_effect = lambda f: os.path.splitext(f)
        mock_os.path.join.side_effect = lambda *args: "/".join(args)
        mock_os.makedirs.return_value = None

        mock_transport = MagicMock()
        mock_sftp = MagicMock()
        mock_paramiko.Transport.return_value = mock_transport
        mock_paramiko.SFTPClient.from_transport.return_value = mock_sftp
        mock_sftp.listdir.return_value = ["file1.txt", "file2.txt"]
        mock_sftp.chdir.return_value = None

        baixar_txt_e_gerar_csv()

        # Não deve baixar/processar nada
        mock_sftp.get.assert_not_called()
        mock_gerar_csv.assert_not_called()
        mock_sftp.close.assert_called()
        mock_transport.close.assert_called()

if __name__ == "__main__":
    unittest.main()