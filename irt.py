import pandas as pd
import girth
import math

import pymysql
import paramiko
from sshtunnel import SSHTunnelForwarder

# membandingkan jawaban siswa dengan kunci jawaban


def periksa(l_kunci, l_jawaban_siswa):

    # memeriksa jawaban siswa terhadap kunci
    # benar = 1
    # salah atau kosong = 0

    l_bs = []  # menyimpan hasil pemeriksaan jawaban siswa
    for i in range(len(l_kunci)):  # loop akan berjalan sebanyak elemen yang ada dalam 'l_kunci'
        # kondisi yang memeriksa jawaban siswa pada indeks [i] sama dengan kunci jawaban pada indeks [i]
        if l_kunci[i] == l_jawaban_siswa[i]:
            # jika jawaban siswa benar, kita menambahkan nilai 1 ke dalam list l_bs
            l_bs.append(1)
        else:
            # jika jawaban siswa salah atau kosong, kita menambahkan nilai 0 ke salam list l_bs
            l_bs.append(0)

    return l_bs  # setelah loop selesai, fungsi mengembalikan list l_bs yang berisi nilai 1 dan 0


# menghitung nilai suatu fungsi matematika yang melibatkan eksponensial dari perbedaan antara kemampuan dan tingkat kesulitan, dan mengembalikan hasil perhitungannya.
def one_var(abil, diff):
    a = abil
    d = diff
    return (math.e**(a-d))/(1+math.e**(a-d))


def sql_data(query, mysql_db):

    # SSH connection details (putty)
    ssh_host = '103.167.112.91'
    ssh_port = 22108
    ssh_username = 'root'
    # ssh_password = 'your_ssh_password'
    private_key_path = 'E:\key\private.ppk'

    # MySQL server details (heidi sql)
    mysql_host = '10.212.37.101'
    mysql_port = 3306
    mysql_username = 'pdkemodul'
    mysql_password = '4lhamdulillaH123'

#     mysql_host = 'localhost'
#     mysql_port = 3306
#     mysql_username = 'root'
#     mysql_password = ''

    # Create an SSH client and connect to the SSH server
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load the private key for authentication
    private_key = paramiko.RSAKey.from_private_key_file(private_key_path)

    # Connect to the SSH server using the private key
    ssh_client.connect(ssh_host, ssh_port, ssh_username, pkey=private_key)

    # Create an SSH tunnel to the MySQL server
    with SSHTunnelForwarder(
            (ssh_host, ssh_port),
            ssh_username=ssh_username,
            ssh_private_key=private_key_path,
            remote_bind_address=(mysql_host, mysql_port)
    ) as tunnel:
        # Connect to the MySQL server through the SSH tunnel
        mysql_conn = pymysql.connect(
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            user=mysql_username,
            password=mysql_password,
            db=mysql_db,
            cursorclass=pymysql.cursors.DictCursor
        )

        cursor = mysql_conn.cursor()

        # Execute a query
        cursor.execute(query)

        if 'SELECT' in query:

            # Fetch the results
            results = cursor.fetchall()

            # Close the cursor
            cursor.close()

            # Close the MySQL connection
            mysql_conn.close()

            # Close the SSH tunnel and SSH connection
            ssh_client.close()
            return results

        elif 'UPDATE' in query:

            # update data
            mysql_conn.commit()

            print(cursor.rowcount, "record(s) affected")

            # Close the cursor
            cursor.close()

            # Close the MySQL connection
            mysql_conn.close()

            # Close the SSH tunnel and SSH connection
            ssh_client.close()


def save_eigen_query(dic_id, dif_list):
    # memperbarui kolom 'eigen' dalam tabel 'soal'
    query = 'UPDATE soal SET eigen = CASE '
    id_string = ''  # untuk menggabungkan daftar ID soal

    # disetiap iterasi loop, kode ini membangun bagian pernyataan CASE dari pernyataan UPDATE. ini menambahkan kondisi 'WHEN' dengan menggabungkan ID soal dan nilai perbedaan yang dibulatkan menjadi dua desimal (2 angka dibelakang koma).
    for i in range(len(dic_id)):
        query = query + "WHEN id_soal = '" + \
            dic_id[i+1][0]+"' THEN '"+str(round(dif_list[i], 2))+"' "

        # memeriksa apakah kita telah mencapai elemen terakhir dalam loop
        if i == len(d_data_ba) - 1:
            id_string = id_string + "'"+dic_id[i+1][0] + "'"
        else:
            id_string = id_string + "'"+dic_id[i+1][0] + "'" + ", "
    # bagian 'END' menutup pernyataan CASE, dan 'id_string' digunakan untuk memfilter baris mana yang akan diperbarui dengan membatasi pada ID soal yang sesuai.
    return query + "END WHERE id_soal IN ("+id_string+")"


# 1. memperoleh data jawaban siswa dari modul digital (db_emodulnf_v3)
kodeba = "X1a2O0123-24PPLS"

query = "SELECT no_nf, list_jawaban FROM tbl_portofolio_ujian WHERE kode_paket = '"+kodeba+"'"
mysql_db = "db_emodulnf_v3"
l_jawaban = sql_data(query, mysql_db)


# 2. memperoleh arr_kodesoal bahan ajar yang di analisis
query = "SELECT arr_kodesoal FROM bahanajar WHERE kodeBahanAjar = '"+kodeba+"'"
arr_kodesoal = sql_data(query, mysql_db)[0]["arr_kodesoal"]

sql_kodesoal = "id_soal = '" + \
    arr_kodesoal.replace(",", "' OR id_soal = '") + "'"

query = "SELECT id_soal, Jawaban FROM soal WHERE "+sql_kodesoal
l = sql_data(query, db1)


# 3. string arr kodesoal = arr_kodesoal
# dictionari kodesoal dan kuncinya = d_idsoal
# dictionari nomor soal, kodesoal dan kuncinya = d_data_ba
# kunci jawaban = kunci


# membuat dic {[id_soal]=jawaban}
d_idsoal = {}
for i in range(len(l)):
    d_idsoal[l[i]["id_soal"]] = l[i]["Jawaban"]


# mendapatkan kunci jawaban sekalian menyusun dictionari
# {[nomor_soal]:[kodesoal,kunci]}
l = arr_kodesoal.split(",")
d_data_ba = {}
l_kunci = []

for i in range(len(l)):
    d_data_ba[i+1] = (l[i], d_idsoal[l[i]])
    l_kunci.append(d_idsoal[l[i]])


# 4. menghitung jawaban siswa menjadi 1, 0 dan menyimpannya dalam dictionari dengan key id_siswa dan value list benar salah (1, 0)
d_jawaban_siswa = {}
for x in l_jawaban:
    id_siswa = x["no_nf"]
    bs_jawaban = periksa(l_kunci, x["list_jawaban"].split(","))
    d_jawaban_siswa[id_siswa] = bs_jawaban


# 5. mengubah data menjadi datafame lalu jadi numpy
df_jawaban = pd.DataFrame.from_dict(d_jawaban_siswa, orient='index')
df_jawaban = df_jawaban.transpose()
np_jawaban = df_jawaban.to_numpy()


# 6. menghitung difficulty
# menghitung difficulty dengan joint maximum
diff_jml = girth.rasch_jml(np_jawaban)

# menghitung ability
abil = girth.ability_mle(
    np_jawaban, diff_jml['Difficulty'], diff_jml['Discrimination'])

# membuat query save eigen
query_save = save_eigen_query(d_data_ba, diff_jml['Difficulty'])


sql_data(query_save, db1)


# CATATAN PENTING
# ==========================================================

# 1. skrip di atas tidak menyimpan data aibility (abil) hanya menyimpan difficulty

# 2. hitung peluang benar setiap soal untuk setiap peserta dengan fungsi one_var
#   0 < peluang <= 0.3   artinya sukar
#   0.3 < peluang < 0.7 artinya sedang
#   0.7 <= peluang < 1 artinya mudah

# 3. untuk portofolio buat tabel
#   id_peserta | ak_mudah_benar | ak_mudah_salah | ak_mudah_kosong | ak_sedang_benar | ak_sedang_salah | ak_sedang_kosong | ak_sukar_benar | ak_sukar_salah | ak_sukar_kosong
#   atau yang semisal dengan itu atau diskusikan dengan kang irwan
#   ak = array_kodesoal

# 4. paramiko dan sshtunnel untuk coneksi ssh.
